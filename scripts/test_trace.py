"""测试 trace_id。"""

import httpx


def main() -> None:
    for i in range(3):
        r = httpx.get("http://localhost:8000/health")
        print(f"请求 {i+1}: {r.headers.get('X-Trace-Id')}")


if __name__ == "__main__":
    main()
