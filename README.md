# 고양 스마트시티즌 방문자 카운터

한 페이지 자기소개 웹사이트에 방문자 수를 붙이는 5·6차시 공통 프로토타입입니다.

브라우저에는 Supabase 키가 없습니다. 브라우저는 같은 출처의 FastAPI에만 요청하고,
FastAPI가 서버 환경변수에 저장된 Supabase secret key로 방문자 수를 1 올립니다.

```text
브라우저 → FastAPI /api/visit → Supabase RPC → 누적 방문자 수
```

## 1. Supabase 준비

1. Supabase 프로젝트에서 **SQL Editor**를 엽니다.
2. [`sql/setup.sql`](sql/setup.sql)의 전체 내용을 붙여넣고 **Run**을 누릅니다.
3. 프로젝트 URL과 서버 전용 secret key를 확인합니다.

secret key는 웹페이지, 화면 캡처, GitHub에 절대 넣지 않습니다.

## 2. 로컬에서 실행

Windows PowerShell 기준입니다.

```powershell
Copy-Item .env.example .env
```

`.env`에서 두 값을 자신의 프로젝트에 맞게 바꿉니다.

```dotenv
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=sb_secret_your_server_only_key
```

의존성을 설치하고 개발 서버를 엽니다.

```powershell
uv sync
uv run fastapi dev app.py
```

Chrome에서 <http://127.0.0.1:8000>을 열어 방문자 수가 보이는지 확인합니다.

## 3. Vercel에 배포

1. 이 폴더를 GitHub 저장소에 올립니다.
2. Vercel에서 **Add New → Project**를 선택하고 저장소를 Import합니다.
3. Environment Variables에 `SUPABASE_URL`, `SUPABASE_SECRET_KEY`를 추가합니다.
4. Deploy를 누릅니다.

배포 주소를 열면 같은 `page_views` 숫자가 증가합니다. 로컬과 온라인이 같은
Supabase 프로젝트를 사용하므로 데이터는 끊어지지 않습니다.

## 확인 명령

```powershell
uv run --group dev pytest
```
