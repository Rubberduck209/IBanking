// ============================================================
// Đổi localhost thành 127.0.0.1 để tránh kẹt mạng
// ============================================================
const USER_API = "http://127.0.0.1:8000";
const TUITION_API = "http://127.0.0.1:8001";
const PAYMENT_API = "http://127.0.0.1:8002";

const TOKEN_KEY = "ibanking_token";

let currentUserId = null;
let currentTuition = null;
let currentTransactionId = null;

const loginView = document.getElementById("login-view");
const dashboardView = document.getElementById("dashboard-view");
const sessionInfo = document.getElementById("session-info");
const sessionName = document.getElementById("session-name");
const logoutBtn = document.getElementById("logout-btn");

const loginForm = document.getElementById("login-form");
const loginSubmit = document.getElementById("login-submit");
const loginError = document.getElementById("login-error");

const payerError = document.getElementById("payer-error");
const payerName = document.getElementById("payer-name");
const payerPhone = document.getElementById("payer-phone");
const payerEmail = document.getElementById("payer-email");
const payerBalance = document.getElementById("payer-balance");


const lookupForm = document.getElementById("lookup-form");
const lookupSubmit = document.getElementById("lookup-submit");
const lookupError = document.getElementById("lookup-error");
const lookupIdle = document.getElementById("lookup-idle");
const lookupResult = document.getElementById("lookup-result");

const ticketStudentName = document.getElementById("ticket-student-name");
const ticketStudentId = document.getElementById("ticket-student-id");
const ticketFeeName = document.getElementById("ticket-fee-name");
const ticketAmount = document.getElementById("ticket-amount");
const ticketStatus = document.getElementById("ticket-status");

const paySubmit = document.getElementById("pay-submit");
const payMessage = document.getElementById("pay-message");
const otpSection = document.getElementById("otp-section");
const otpInput = document.getElementById("otp-input");
const otpSubmit = document.getElementById("otp-submit");

const historyIdle = document.getElementById("history-idle");
const historyError = document.getElementById("history-error");
const historyTable = document.getElementById("history-table");
const historyBody = document.getElementById("history-body");

function showBanner(el, message) {
  el.textContent = message;
  el.classList.remove("hidden");
}

function hideBanner(el) {
  el.classList.add("hidden");
  el.textContent = "";
}

function formatVND(amount) {
  const n = Number(amount);
  if (Number.isNaN(n)) return String(amount);
  return n.toLocaleString("vi-VN") + " ₫";
}

function getToken() { return localStorage.getItem(TOKEN_KEY); }
function setToken(token) { localStorage.setItem(TOKEN_KEY, token); }
function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  currentUserId = null;
  currentTuition = null;
}

function setLoading(button, isLoading, idleLabel) {
  button.disabled = isLoading;
  button.textContent = isLoading ? "Đang xử lý…" : idleLabel;
}

function getUserIdFromToken(token) {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.user_id;
  } catch (e) {
    return null;
  }
}

function showLogin() {
  loginView.classList.remove("hidden");
  dashboardView.classList.add("hidden");
  sessionInfo.classList.add("hidden");
}

function showDashboard() {
  loginView.classList.add("hidden");
  dashboardView.classList.remove("hidden");
  sessionInfo.classList.remove("hidden");
}

async function apiLogin(username, password) {
  const res = await fetch(`${USER_API}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Đăng nhập thất bại.");
  return data;
}

async function apiGetPayerInfo(token) {
  const res = await fetch(`${USER_API}/users/me/payer-info`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json().catch(() => ({}));
  if (res.status === 401) {
    const err = new Error(data.detail || "Phiên đăng nhập đã hết hạn.");
    err.unauthorized = true;
    throw err;
  }
  if (!res.ok) throw new Error(data.detail || "Không lấy được thông tin người dùng.");
  return data;
}

async function apiGetTuition(studentId) {
  const res = await fetch(`${TUITION_API}/api/tuitions/${encodeURIComponent(studentId)}`);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Không tra cứu được thông tin học phí.");
  return data;
}

async function apiCreateTransaction(userId, studentId, amount, token) {
  const res = await fetch(`${PAYMENT_API}/transactions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      user_id: Number(userId),
      student_id: String(studentId),
      amount: Number(amount)
    })
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401) {
      const err = new Error(data.detail || "Phiên đăng nhập đã hết hạn.");
      err.unauthorized = true;
      throw err;
    }
    throw new Error(data.detail || "Thanh toán thất bại.");
  }
  return data;
}

async function apiVerifyOtp(transactionId, otpCode, token) {
  const res = await fetch(`${PAYMENT_API}/transactions/verify-otp`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ transaction_id: transactionId, otp_code: otpCode })
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || "Xác thực OTP thất bại.");
  return data;
}

async function apiGetMyTransactions(token) {
  const res = await fetch(`${PAYMENT_API}/transactions/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const data = await res.json().catch(() => ([]));
  if (res.status === 401) {
    const err = new Error("Phiên đăng nhập đã hết hạn.");
    err.unauthorized = true;
    throw err;
  }
  if (!res.ok) throw new Error(data.detail || "Không lấy được lịch sử giao dịch.");
  return data;
}

const STATUS_LABEL = {
  PENDING: "Đang xử lý",
  SUCCESS: "Thành công",
  EXPIRED: "Hết hạn OTP",
};

function renderHistory(transactions) {
  if (!transactions.length) {
    historyTable.classList.add("hidden");
    historyIdle.classList.remove("hidden");
    return;
  }
  historyIdle.classList.add("hidden");
  historyTable.classList.remove("hidden");

  historyBody.innerHTML = transactions.map(t => {
    const time = new Date(t.created_at).toLocaleString("vi-VN");
    const label = STATUS_LABEL[t.status_] || t.status_;
    return `
      <tr style="border-bottom: 1px solid var(--line); white-space: nowrap;">
        <td style="padding:12px 6px;">${time}</td>
        <td style="padding:12px 6px;" class="mono">${t.student_id}</td>
        <td style="padding:12px 6px;">${formatVND(t.amount)}</td>
        <td style="padding:12px 6px;">${label}</td>
      </tr>`;
  }).join("");
}

async function loadHistory() {
  hideBanner(historyError);
  const token = getToken();
  if (!token) return;
  try {
    const transactions = await apiGetMyTransactions(token);
    renderHistory(transactions);
  } catch (err) {
    if (err.unauthorized) {
      clearToken(); showLogin(); showBanner(loginError, err.message); return;
    }
    showBanner(historyError, err.message);
  }
}

async function loadPayerInfo() {
  hideBanner(payerError);
  const token = getToken();
  if (!token) return;

  currentUserId = getUserIdFromToken(token);

  try {
    const payer = await apiGetPayerInfo(token);
    payerName.textContent = payer.full_name || "—";
    payerPhone.textContent = payer.phone_number || "—";
    payerEmail.textContent = payer.email || "—";
    payerBalance.textContent = formatVND(payer.available_balance);
    sessionName.textContent = `Xin chào, ${payer.full_name || ""}`;
  } catch (err) {
    if (err.unauthorized) {
      clearToken(); showLogin(); showBanner(loginError, "Phiên đăng nhập đã hết hạn."); return;
    }
    showBanner(payerError, err.message);
  }
}

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideBanner(loginError);
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  setLoading(loginSubmit, true, "Đăng nhập");
  try {
    const { access_token } = await apiLogin(username, password);
    setToken(access_token);
    loginForm.reset();
    showDashboard();
    await loadPayerInfo();
    await loadHistory();
  } catch (err) {
    showBanner(loginError, err.message);
  } finally {
    setLoading(loginSubmit, false, "Đăng nhập");
  }
});

logoutBtn.addEventListener("click", () => {
  clearToken();
  lookupResult.classList.add("hidden");
  lookupIdle.classList.remove("hidden");
  lookupForm.reset();
  showLogin();
});

lookupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideBanner(lookupError);
  hideBanner(payMessage);

  lookupResult.classList.add("hidden");
  lookupIdle.classList.add("hidden");
  paySubmit.disabled = false;

  const studentId = document.getElementById("student-id").value.trim();
  if (!studentId) return;

  setLoading(lookupSubmit, true, "Tra cứu");
  try {
    const tuition = await apiGetTuition(studentId);
    currentTuition = tuition;

    ticketStudentName.textContent = tuition.student_name || "—";
    ticketStudentId.textContent = tuition.student_id || studentId;
    ticketFeeName.textContent = tuition.tuition_fee_name || "Học phí";
    ticketAmount.textContent = formatVND(tuition.amount_due);
    ticketStatus.textContent = "Còn phải đóng";
    ticketStatus.style.background = "var(--success-bg)";
    ticketStatus.style.color = "var(--success)";

    lookupResult.classList.remove("hidden");
  } catch (err) {
    lookupIdle.classList.remove("hidden");
    showBanner(lookupError, err.message);
    currentTuition = null;
  } finally {
    setLoading(lookupSubmit, false, "Tra cứu");
  }
});

paySubmit.addEventListener("click", async () => {
  hideBanner(payMessage);
  const token = getToken();

  if (!token || !currentUserId || !currentTuition) {
    alert("Lỗi: Mất thông tin phiên làm việc. Vui lòng nhấn F5 tải lại trang!");
    return;
  }

  setLoading(paySubmit, true, "Xác nhận thanh toán");
  try {
    const result = await apiCreateTransaction(
      currentUserId,
      currentTuition.student_id,
      currentTuition.amount_due,
      token
    );

    payMessage.className = "banner banner-success";
    showBanner(payMessage, `Khởi tạo giao dịch thành công. Trạng thái: ${result.status_}. Vui lòng chờ nhập mã OTP.`);
    paySubmit.disabled = true;

    ticketStatus.textContent = "Đang xử lý (PENDING)";
    ticketStatus.style.background = "#FEF08A";
    ticketStatus.style.color = "#854D0E";

    currentTransactionId = result.transaction_id;
    otpSection.classList.remove("hidden");
  } catch (err) {
    if (err.unauthorized) {
      clearToken(); showLogin(); showBanner(loginError, err.message); return;
    }
    payMessage.className = "banner banner-error";
    showBanner(payMessage, err.message);
  } finally {
    setLoading(paySubmit, false, "Xác nhận thanh toán");
  }
});

otpSubmit.addEventListener("click", async () => {
  const token = getToken();
  const code = otpInput.value.trim();
  if (!code || !currentTransactionId) return;

  setLoading(otpSubmit, true, "Xác nhận OTP");
  try {
    const result = await apiVerifyOtp(currentTransactionId, code, token);
    payMessage.className = "banner banner-success";
    showBanner(payMessage, result.detail || "Thanh toán thành công!");
    otpSection.classList.add("hidden");
    ticketStatus.textContent = "Đã thanh toán";
    ticketStatus.style.background = "var(--success-bg)";
    ticketStatus.style.color = "var(--success)";
    loadHistory();
  } catch (err) {
    payMessage.className = "banner banner-error";
    showBanner(payMessage, err.message);
  } finally {
    setLoading(otpSubmit, false, "Xác nhận OTP");
  }
});

(function init() {
  const token = getToken();
  if (token) {
    showDashboard();
    loadPayerInfo();
    loadHistory();
  } else {
    showLogin();
  }
})();