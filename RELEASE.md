# Release Checklist and Instructions

本文件描述如何准备、构建、测试、打 tag 和发布本项目的发行版（wheel / sdist）。

当前版本：`0.1.0`（见 `VERSION` 文件）

1) 预发布检查

- 确保测试通过（如果存在测试）：

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install pytest
pytest -q
```

- 运行 smoke tests（仓库中 `examples/` 里有示例）：

```bash
python3 examples/smoke_test.py
python3 examples/smoke_test_real.py
```

- 确认代理可以启动并响应：

```bash
GEMINI_PATH=/path/to/gemini python3 -m uvicorn proxy:app --host 127.0.0.1 --port 7777 --log-level info
curl -sS http://127.0.0.1:7777/health
curl -sS http://127.0.0.1:7777/v1/models
```

2) 更新版本与变更日志

- 修改 `VERSION` 为新的版本号（如 `0.1.1`），并在 `CHANGELOG.md` 中新增条目。

3) 构建 wheel / sdist

```bash
python3 -m pip install --upgrade build
python3 -m build
# 产物位于 dist/
```

4) 本地安装测试

```bash
python3 -m venv /tmp/gp-venv && source /tmp/gp-venv/bin/activate
pip install dist/gemini_proxy-0.1.0-py3-none-any.whl
python -c "import proxy; print('proxy.app exists:', hasattr(proxy,'app'))"
```

5) Git 提交、打 tag 并推送

```bash
git add -A
git commit -m "chore(release): v0.1.0"
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main
git push origin v0.1.0
```

6) 在 GitHub 上创建 Release 并上传 artifacts（推荐使用 `gh` CLI）

如果你安装并登录了 `gh`：

```bash
gh release create v0.1.0 dist/* --title "v0.1.0" --notes-file CHANGELOG.md
```

如果没有 `gh`，也可以在 GitHub UI 上创建 Release，然后上传 `dist/` 下的文件作为 Attachments。

7) 上传到 PyPI（可选）

```bash
python3 -m pip install --upgrade twine
python3 -m twine upload dist/*
```

或上传到 testpypi：

```bash
python3 -m twine upload --repository testpypi dist/*
```

8) 部署示例（systemd）以及验证方法参见仓库根目录的早期文档。

如果你希望，我可以：
- 在本地为你运行 `gh release create` 并上传 `dist/*`（前提是 `gh` 已安装且你已登录）；
- 或者输出你可以复制粘贴到终端的一组命令来完成发布流程。
# Release Checklist and Instructions

This document describes steps to prepare, build, test, tag, and publish a release for the Gemini-CLI FastAPI proxy.

Current version: `0.1.0` (see `VERSION`)

## 1. Pre-release checks

- Ensure tests are passing (if you have tests):

```bash
python3 -m pip install -r requirements.txt
python3 -m pip install pytest
pytest -q
```

- Run smoke tests locally (the repository contains `smoke_test.py` and `smoke_test_real.py`):

```bash
python3 smoke_test.py
python3 smoke_test_real.py
```

- Verify the proxy runs and responds:

```bash
GEMINI_PATH=/path/to/gemini python3 -m uvicorn proxy:app --host 127.0.0.1 --port 7777 --log-level info
curl -sS http://127.0.0.1:7777/health
curl -sS http://127.0.0.1:7777/v1/models
```

## 2. Update version and changelog

- Update `VERSION` to the next version (e.g. `0.1.1`) and add an entry to `CHANGELOG.md`.

## 3. Build a wheel / sdist

Install build tooling and create distributions:

```bash
python3 -m pip install --upgrade build
python3 -m build
```

Artifacts will be placed in `dist/` (e.g. `dist/gemini-proxy-0.1.0-py3-none-any.whl`).

## 4. Local install test

Test installing the built wheel into a fresh venv:

```bash
python3 -m venv /tmp/gp-venv
source /tmp/gp-venv/bin/activate
pip install dist/gemini_proxy-0.1.0-py3-none-any.whl
python -c "import proxy; print('imported proxy app')"
```

Adjust file name to match created artifact.

## 5. Git tag & push

Create an annotated tag and push it:

```bash
git add -A
git commit -m "chore(release): v0.1.0"
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin main
git push origin v0.1.0
```

If you use a different branch name than `main`, replace accordingly.

## 6. Create GitHub Release (optional)

Use the GitHub UI or hub/gh CLI:

```bash
gh release create v0.1.0 dist/* --title "v0.1.0" --notes-file CHANGELOG.md
```

## 7. Upload to PyPI (optional)

Be careful — this publishes the package publicly. Configure your `~/.pypirc` with PyPI credentials or use `twine` with token.

```bash
python3 -m pip install --upgrade twine
python3 -m twine upload dist/*
```

For test PyPI:

```bash
python3 -m twine upload --repository testpypi dist/*
```

## 8. Deploy to a server (example systemd)

An example `systemd` unit to run the app on a server as a service:

```
[Unit]
Description=Gemini Proxy
After=network.target

[Service]
User=youruser
Group=yourgroup
WorkingDirectory=/opt/gemini-proxy
Environment=GEMINI_PATH=/opt/homebrew/bin/gemini
ExecStart=/usr/bin/env uvicorn proxy:app --host 0.0.0.0 --port 7777 --workers 1
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Copy this to `/etc/systemd/system/gemini-proxy.service`, reload systemd and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gemini-proxy
sudo journalctl -u gemini-proxy -f
```

## 9. Verification after deployment

- Check health endpoint:

```bash
curl -sS http://server-ip:7777/health
```

- Trigger a sample chat completion (non-streaming):

```bash
curl -sS -X POST http://server-ip:7777/v1/chat/completions -H "Content-Type: application/json" -d '{"model":"gemini-2.5-pro-preview-06-05","messages":[{"role":"user","content":"你好"}]}'
```

- Check logs (`proxy.log` and systemd journal) for errors.

## 10. Rollback strategy

If release causes issues, roll back by re-deploying the previous tag or switching the unit file to an earlier artifact.

```bash
git checkout v0.0.1
# redeploy older artifact
```

## 11. Post-release

- Open any follow-up issues for improvements (logging rotation, auth, HTTPS termination, monitoring).

---

If你希望，我可以：
- 立刻基于 `pyproject.toml` 执行 `python -m build` 生成 `dist/`；或
- 帮你生成一个 GitHub Actions workflow 来在 push 时自动构建并发布到 testpypi；或
- 把 `RELEASE.md` 内容合并到 `README.md` 的发布节中。

告诉我你接下来想做哪一步，我会继续执行。