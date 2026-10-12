# Geo-Guesser

> 简体中文 · [English](README.md)

一组**中国大陆网络环境下的变通工具**，服务于 [geo-sleuth](https://github.com/Oldcircle/geo-sleuth)
（一个 MIT 协议的照片地理定位 agent skill）。本仓库**不是** geo-sleuth 的 fork——
它做补充：当你从中国大陆运行该 skill 时，默认的 Google/ESRI 卫星图源和部分引擎
是不可达的。

## 为什么需要它

`geo-sleuth` 假设你可以访问全球网络。在国内机器上：

- Google 和 ESRI 卫星瓦片会超时（无代理）→ `tiles.py` / `sat_scan.py` 卡住。
- 百度以图搜图仍然可用，且通常足以命名地点。
- 百度街景在景区内部没有覆盖。

这些辅助脚本在不触碰上游 skill 的前提下，恢复了一条可用的工作流。

## 快速开始 — 约 3 分钟定位一张照片

**作答协议（两条通道通用）：** 每张照片在看到后 **~10 秒内先给出第一答案**——
国家/城市 + 置信度 + 一句理由——在任何 prep 输出被读取之前；后续证据再以
confirms / refines / overturns 的方式修正，且修正链保持可见。协议见
`FIRST_ANSWER.md`。

一条命令版本（单次调用完成 run 目录、后台 intake、board 和招牌裁切，然后打印
带时间轴的后续步骤）：

```bash
bash gg_fast.sh photo.jpg run1
```

前提是 geo-sleuth 已安装在 `~/.workbuddy/skills/geo-sleuth`（见「环境要求」），
并且你有一张照片，例如 `photo.jpg`：

```bash
# 0) 指向 geo-sleuth skill
export CLAUDE_SKILL_DIR="$HOME/.workbuddy/skills/geo-sleuth"
S="$CLAUDE_SKILL_DIR/scripts"

# 1) 后台启动快速 intake（~60s；仅百度、关 OCR）
uv run "$S/intake.py" photo.jpg --out-dir intake/ --no-ocr --engines baidu &

# 2) intake 运行期间，并行准备候选 board + 边缘裁切
RUN=<your-run-dir>; cd "$RUN"
uv run "$S/board.py" init --photo photo.jpg
uv run "$S/board.py" country cn          # 未知国家时跳过
uv run "$S/imgprep.py" edges photo.jpg --out-dir edges/
wait                                      # 3) intake/intake.md 就绪

# 4) 读取百度投票结果 + 联系表（intake/rev/photo_baidu_similar.jpg）
#    -> 对多数国内照片，这一步就能定位到国家/城市/区域级
```

可选后续（超出 3 分钟预算）：

```bash
# 用卫星镶嵌图核对道路布局
uv run --with pillow amap_sat.py <lat> <lon> 18 2 sat.jpg
# 合成一页可分享的证据图
uv run --with pillow evidence_sheet.py my_case.json evidence.jpg
```

## 适用范围：国内通道 vs 全球通道

| 工具 | 适用范围 | 说明 |
|---|---|---|
| `gg_fast.sh` | **国内通道** | 仅百度 intake、关 OCR；百度对国内场景最强 |
| `amap_sat.py` | **仅国内影像** | 高德海外瓦片返回"无卫星影像"占位图（已实测） |
| `phone_lookup.py` | 🌍 **全球、离线** | 内置 libphonenumber 地理数据；零网络，不怕 GFW |
| `sat_global.py` | 🌍 全球 | ESRI/Google 瓦片；国内运行时设 `GEO_PROXY` 指向你的代理 |
| `global_accuracy.sh` | 🌍 全球 | 精度优先的 prep 通道 + SOP，`REGION` 速度分档 |
| `script_route.py` / `driving_side.py` / `sun_hint.py` | 🌍 全球 | step-0 区域排除器（文字系统 / 左右行 / 半球） |
| `pin_title_mine.py` | 🌍 全球 | 挖掘百度反查源页标题中的地名（~30s） |
| `gg_prep_batch.sh` | 🌍 全球 | 批量照片的错峰并行 prep |
| `evidence_sheet.py` | 🌍 全球 | 纯本地图片合成 |

**经验法则：** 国内照片 → 国内通道（`gg_fast.sh` + `amap_sat.py`）。
其余 → 全球通道（`global_accuracy.sh` + `sat_global.py`），如果在国内运行需
export `GEO_PROXY`。`phone_lookup.py` 和 `evidence_sheet.py` 两条通道都能用。

### 全球通道 — 实测数据（2026-10-12，国内网络）

对 4 张照片做了盲测（巴黎街巷 / 东京天际线 / 摩洛哥 ksar / 墨西哥城 Zocalo），
两条通道、同一份封存真值：

| | v1（只用图像引擎） | v2（精度优先：`global_accuracy.sh` + SOP） |
|---|---|---|
| 国家 | 3/4 | **4/4** |
| 城市 | 2/4 | **3/4** |
| 具体点位（街道/广场/景点） | 1/4 | **3/4** |

数字是被什么拉起来的：
- **巴黎**（原本国家级 FAIL）：百度在普通外国街巷上是死路（4/4 变体都返回
  同一个纯视觉标签）。**溯源**救了场——照片的原始图库页面标题写着
  "Rue de Ravignan: Montmartre Street" → 街道级命中，坐标已验证。
- **摩洛哥**（城市原本答错）：百度说是舍夫沙万；agent 视觉判定（土黄色 ksar，
  不是蓝色城市）+ 一条携程来源写明阿伊特本哈杜 → 正确景点，坐标已验证。
- 东京 / 墨西哥城本来就对，带着更硬的证据保持正确。

已实测的死路（不要盲目重试）：Google Lens、TinEye、Mapillary、KartaView、
cn.bing 视觉上传、Yandex 以图搜图、变体百度补救、对外国 POI 用 `poi.py`。
真正管用的：**Yandex 网页搜索（经 WebFetch）、服务端 WebSearch/WebFetch、
溯源、系统化的 agent 视觉判读。**
完整数据：`CHINA_NETWORK_NOTES.md`（"Engine availability probed"、
"Global lane retest" 两节）。

### 全球通道 — 速度（实测 2026-10-12, v3）

`global_accuracy.sh` 支持按区域设**速度分档**——百度变体反搜只在东南亚/东亚
有回报（中文旅游博客覆盖），在目前所有北美/欧洲照片上返回的都是噪声，所以
这些区域砍掉变体：

| 分档 | 百度反搜范围 | 每张 prep 耗时 | 适用 |
|---|---|---|---|
| `full`（auto 默认） | photo + flip + gray + wb | ~105s | 未知照片、非拉丁文字 |
| `sea` | photo + flip | ~80s | 东南亚/东亚/南亚 |
| `eu` / `na` | 仅 photo | **~61–64s** | 欧洲 / 美洲 |

```bash
# 单张，强制分档
REGION=eu bash global_accuracy.sh photo.jpg run_eu

# 批量：错峰并行 prep（2 张总墙钟 72s）
REGION=sea bash gg_prep_batch.sh --stagger 8 *.jpg
```

prep 之后，最快的准确率杠杆通常是 `pin_title_mine.py .`（挖掘百度源页标题中的
地名，~30s）。auto 路由刻意保守：纯文本路由无法区分欧洲和美洲，所以看 5 秒照片
后自己设 `REGION` 更靠谱。

## 仓库内容

### 通道启动器（先跑这些）

| 文件 | 作用 |
|---|---|
| `gg_fast.sh` | 一条命令的**国内快速通道**：run 目录 + 后台仅百度 intake + board + 招牌裁切，打印带时间轴的 SOP（端到端 ~3 分钟）。 |
| `global_accuracy.sh` | **全球精度通道**：全量 intake（开 OCR）+ 精细 OCR 补扫 + 各变体百度反搜 + 区域排除器；`REGION=auto\|sea\|eu\|na\|full` 速度分档。 |
| `gg_prep_batch.sh` | 一批照片的错峰**并行 prep**（2 张：~72s 墙钟 vs 串行 ~210s）。 |

### 分析工具（prep 期间/之后跑）

| 文件 | 作用 |
|---|---|
| `pin_title_mine.py` | 挖掘百度反查源页（duitang/huaban/tuchong/699pic…）中的**地名**——单步产出最高（~30s）。 |
| `phone_lookup.py` | **离线全球电话号码定位**（libphonenumber）。招牌上的号码零网络锁定国家 + 城市。 |
| `script_route.py` | 文字系统 → **候选区域 + OCR 语言**（Unicode 区间，无依赖）。 |
| `driving_side.py` | **左行/右行排除器**——约 75 个左行国家/地区 + 看不到方向盘时的目视判读方法。 |
| `sun_hint.py` | 由 EXIF GPS+时间或实测影子方位做**半球/纬度带收窄**；包装 geo-sleuth 的 `sun.py`。 |
| `sat_global.py` | 中国以外地区的全球卫星镶嵌图（ESRI/Google），支持 `GEO_PROXY`，`--dry-run` 可验证瓦片计算。 |
| `amap_sat.py` | **高德**卫星镶嵌图，国内可达（已处理 WGS84→GCJ-02）。 |
| `evidence_sheet.py` | 从 JSON 规格合成可分享的证据图（裁切 + 说明 + 结论）。 |

### 手册与记录（读这些）

| 文件 | 作用 |
|---|---|
| `FIRST_ANSWER.md` | 作答协议：~10s 内给出第一答案，再以可见的 confirms/refines/overturns 链修正。 |
| `GLOBAL_ACCURACY_SOP.md` | 海外 agent 手册：引擎地图、步骤顺序（第一答案 → 路由 → 通读 → 文字 → 溯源 → 验证）、照片类型决策表。 |
| `VISION_CLUES.md` | 系统化目视判读清单（文字、左右行、车牌、电线杆、建筑、植被…）+ 国内相似图偏置陷阱。 |
| `GLOBAL_OPTIMIZATION.md` | 海外精度路线图：已实测死路 + 8 条按性价比排序的优化路径及状态。 |
| `CHINA_NETWORK_NOTES.md` | 实测网络约束（国内什么可达）与 3 分钟工作流。 |
| `TEST_REPORT_V3.md` | v3 海外盲测：4 张照片，国家 4/4、城市 3/4——每次命中靠的是什么。 |
| `README.zh-CN.md` | 本文件，README 的中文版。 |
| `examples/zhangjiajie_evidence.json` | 来自真实张家界案例的 `evidence_sheet.py` 规格示例。 |

## 环境要求

- `uv`（https://docs.astral.sh/uv/）
- 已安装 geo-sleuth：`https://github.com/Oldcircle/geo-sleuth`
  （默认安装位置假定为 `~/.workbuddy/skills/geo-sleuth`；可用
  `GEO_SLEUTH_SKILL=/path/to/geo-sleuth` 覆盖）。

## 用法

### 快速 intake（仅百度，~60s，不阻塞）

```bash
# 放后台跑，以便并行准备 board
export GEO_SLEUTH_SKILL="$HOME/.workbuddy/skills/geo-sleuth"
uv run "$GEO_SLEUTH_SKILL/scripts/intake.py" photo.jpg --out-dir intake/ --no-ocr --engines baidu &

# 同时在另一个 shell 里：
export CLAUDE_SKILL_DIR="$HOME/.workbuddy/skills/geo-sleuth"
uv run "$CLAUDE_SKILL_DIR/scripts/board.py" init --photo photo.jpg
uv run "$CLAUDE_SKILL_DIR/scripts/board.py" country cn
uv run "$CLAUDE_SKILL_DIR/scripts/imgprep.py" edges photo.jpg --out-dir edges/
wait   # intake/intake.md 生成后，读取百度投票结果 + 联系表
```

### 高德卫星兜底

```bash
uv run --with pillow amap_sat.py 29.3454 110.4648 18 2 amap_srsm18.jpg
# 参数：<lat> <lon> [zoom=17] [radius=2] [out]
# zoom 17-18 可辨单条道路/建筑；radius=2 -> 5x5 镶嵌图
```

### 证据图

```bash
uv run --with pillow evidence_sheet.py examples/zhangjiajie_evidence.json evidence.jpg
# 规格 JSON：title、可选 base dir、rows[{images,height,caption}]、footer[]
```

### 全球模式（精度优先——不计时）

```bash
# 1) prep：全量 intake（开 OCR）+ 精细 OCR 补扫（3x3 分块、3 倍上采样）
#    + 对每个变体（crop/flip/gray/wb）做百度反搜
#    ~3-6 分钟；放后台跑
bash global_accuracy.sh paris.jpg run_paris

# 2) 然后按 GLOBAL_ACCURACY_SOP.md 的顺序执行：
#    - 通读一切；边看照片边对照 VISION_CLUES.md
#    - 文字优先：号码用 phone_lookup.py（离线、即时）；
#      名称用 WebSearch / Yandex 网页搜索（经 WebFetch）（国内均可用）
#    - 溯源：任何 URL / 文件名 / 水印 / EXIF 线索 ->
#      WebFetch 源页面；图注往往直接写了地名。单这一步就把巴黎盲测
#      从国家级 FAIL 变成了街道级命中。
#    - 验证：poi.py + sat_global.py（需 GEO_PROXY）/ amap_sat.py（国内）

# 3) 离线电话号码定位（两条通道通用）
uv run --with phonenumbers phone_lookup.py 13758466320 +33142685300

# 4) 全球卫星镶嵌图（默认 ESRI；国内需加代理）
GEO_PROXY=http://127.0.0.1:<port> uv run --with pillow sat_global.py 48.8584 2.2945 17 1 paris.jpg
```

为什么是这个形态：国内实测下，没有任何额外的图像引擎可达
（google lens / yandex-reverse / tineye / mapillary 全死）。因此海外精度来自
**文字搜索 + 溯源 + 系统化的 agent 视觉判读**，而不是更多以图搜图引擎。

## 许可证

MIT——与 geo-sleuth 相同。本仓库只添加了中国特有的辅助脚本，不修改上游 skill。
