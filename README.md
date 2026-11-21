# FlangeGetData · 管路智选

法兰、垫片、钢管、管件规格查询与机械选型工具。主程序位于 `FlangeQueryV2/`，当前版本 V3.78.0。

- 项目说明：`FlangeQueryV2/README.md`
- 更新记录：`FlangeQueryV2/CHANGELOG.md`
- 程序入口：`FlangeQueryV2/main.py`
- 构建入口：`FlangeQueryV2/tools/build_release.py`

快速验证：

```bat
cd FlangeQueryV2
python -m unittest discover -s tests -v
```

发布前请以 `FlangeQueryV2/tools/build_release.py` 重新构建，避免直接分发旧的 `dist/` 或 zip。数据校核事项见项目 README。
