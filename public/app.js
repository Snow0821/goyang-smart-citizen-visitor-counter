const countElement = document.querySelector("#visitor-count");
const statusElement = document.querySelector("#counter-status");
const environmentElement = document.querySelector("#environment-pill");

const isLocal = ["localhost", "127.0.0.1"].includes(window.location.hostname);
environmentElement.textContent = isLocal
  ? "로컬 FastAPI에서 확인 중"
  : "Vercel에서 확인 중";

async function recordVisit() {
  try {
    const response = await fetch("/api/visit", { method: "POST" });

    if (!response.ok) {
      throw new Error(`방문 기록 실패: ${response.status}`);
    }

    const data = await response.json();
    countElement.textContent = Number(data.count).toLocaleString("ko-KR");
    statusElement.textContent = "같은 Supabase 숫자를 확인했습니다.";
  } catch (error) {
    console.error(error);
    countElement.textContent = "?";
    statusElement.textContent = "연결을 확인한 뒤 페이지를 새로고침해 주세요.";
    statusElement.classList.add("error");
  }
}

recordVisit();
