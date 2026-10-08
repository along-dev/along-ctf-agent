# 01 路径、编码、CRLF

## CRLF 铁律

- `.cmd` / `.bat` 必须 **CRLF 换行 + 纯 ASCII**。
- `cmd.exe` 按 OEM 代码页解析，LF 会导致行解析错位，UTF-8 中文注释会乱码/错行。
- 被 git 或编辑器转成 LF 后要转回：`unix2dos` 或编辑器改行尾。

## 中文路径与编码

- Python 入口先 `sys.stdout.reconfigure(encoding="utf-8")`，否则 GBK 控制台抛 UnicodeEncodeError。
- 文件读写显式 `encoding="utf-8"`。
- 路径含空格/中文时，`.cmd` 里用引号包裹，`%~dp0` 自带尾反斜杠注意拼接。

## 常见坑

| 坑 | 修 |
|---|---|
| 中文注释导致 .cmd 错行 | 注释改英文，或删注释 |
| 中文输出乱码 | chcp 65001 或 reconfigure utf-8 |
| 路径空格断命令 | 引号包裹路径 |
