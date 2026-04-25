# mlx-serve

本机 Apple Silicon 上运行的 ASR（语音转文字）HTTP 服务，基于 MLX 框架推理。

## 快速启动

```bash
cp config.example.yaml config.yaml   # 从模板创建配置，按需填入 hf_token
make install                         # 安装依赖
make run                             # 启动服务（默认绑定 0.0.0.0:8000）
```

服务仅接受本机（`127.0.0.1`）和 Lume 虚拟机子网（`192.168.64.0/24`）的请求，其他来源返回 `403`。

---

## HTTP 接口

### `GET /health`

检查服务状态。

**响应示例：**
```json
{"status": "ok", "model": "mlx-community/Qwen3-ASR-1.7B-8bit"}
```

---

### `POST /transcribe`

上传音频文件，返回转录文本。

**请求：** `multipart/form-data`，字段名 `file`

**查询参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `include_segments` | bool | `false` | 是否返回带时间戳的分段信息。省略时只返回 `text`，减少传输开销 |

**支持格式：** `wav`, `mp3`, `flac`, `m4a`, `aac`, `ogg`, `opus`

**curl 示例：**
```bash
# 仅获取全文
curl -X POST http://127.0.0.1:8000/transcribe \
  -F "file=@audio.wav"

# 包含分段信息
curl -X POST "http://127.0.0.1:8000/transcribe?include_segments=true" \
  -F "file=@audio.wav"
```

**响应：**
```json
{
  "text": "完整转录文本（所有片段拼接）",
  "segments": [
    {"text": "第一句话", "start": 0.0, "end": 3.2, "language": "Chinese"},
    {"text": "The second sentence", "start": 3.2, "end": 6.1, "language": "English"}
  ],
  "language": "Chinese",
  "processing_time": 2.85
}
```

**字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `text` | string | 完整转录全文，即使多语言混合也是所有片段拼接的完整结果 |
| `segments` | array\|null | 带时间戳的分段列表（仅 `include_segments=true` 时返回），用于字幕制作、时间对齐或区分多语言片段 |
| `segments[].text` | string | 该片段的文本 |
| `segments[].start` | float | 片段开始时间（秒） |
| `segments[].end` | float | 片段结束时间（秒） |
| `segments[].language` | string\|null | 该片段识别到的语言 |
| `language` | string\|null | 整体主要语言 |
| `processing_time` | float | 推理耗时（秒） |

**错误码：**

| 状态码 | 原因 |
|--------|------|
| 400 | 不支持的文件格式或空文件 |
| 403 | 来源 IP 不在允许列表 |
| 413 | 文件超过大小限制 |
| 500 | 推理失败 |

---

## 配置

复制 `config.example.yaml` 为 `config.yaml` 并按需修改：

```yaml
server:
  host: "0.0.0.0"
  port: 8000

model:
  name: "mlx-community/Qwen3-ASR-1.7B-8bit"
  hf_token: ""          # 留空则不设置；也可通过环境变量 HF_TOKEN 覆盖

security:
  allowed_cidrs:
    - "127.0.0.1/32"
    - "192.168.64.0/24"

upload:
  max_bytes: 52428800   # 50 MB，-1 表示不限制
  allowed_extensions:
    - wav
    - mp3
    - flac
    - m4a
    - aac
    - ogg
    - opus
```

也可通过 CLI 参数临时覆盖：

```bash
python run.py --config config.yaml --host 127.0.0.1 --port 9000
```
