# DrawingSpec 与矢量输出

> 版本：3.16.0（2026-10-25）
> 目标：把“直接画 QPixmap”升级为“先描述图纸，再渲染到屏幕/PDF/SVG”。

## 一、DrawingSpec

`drawspec/spec.py`：

```text
DrawingSpec
  ├─ PathSpec       轮廓/填充/虚线
  ├─ DimensionSpec  尺寸线、引出点、文字位置
  ├─ TextSpec       标题/说明
  └─ width/height/source
```

特点：

- 绘图数据与 Qt 控件解耦；
- 同一份 spec 可渲染到 `QPixmap`、`QPdfWriter`、`QSvgGenerator`；
- 尺寸文字有独立坐标，可交给布局器避让。

## 二、尺寸布局引擎

`drawspec/layout.py`：

- `DimensionLayout.place_horizontal()`：为顶部横向尺寸选择不重叠的“道”；
- `DimensionLayout.place_vertical()`：为左右竖向尺寸选择不重叠的“道”；
- 用 `QFontMetrics` 计算文字矩形，记录已占用区域；
- 超出画布或碰撞时自动换道。

当前法兰的 `D/K/N/H/C` 已走布局器；弯头的 `R/H/D` 使用显式位置。

## 三、矢量输出

`drawspec/renderer.py`：

```python
render_pixmap(spec)   # 屏幕/测试
save_pdf(spec, path)  # QPdfWriter，A4，300 DPI
save_svg(spec, path)  # QSvgGenerator
```

界面：

- 顶栏新增「📐 矢量图」；
- 选择当前行后，可导出 `.pdf` 或 `.svg`；
- 已支持：
  - 法兰：WN/SO/PL/SW/Th/BL/IF/LWN/623；
  - 弯头：45°/90°/180°；
- 当前页暂不支持的图种会提示，不会生成空文件。

## 四、PageSpec 扩展

`core/page_spec.py` 保持前 4 字段的 4 元组解包兼容：

```python
name, csvf, template, labels = page
```

新增可选字段：

```text
code / group / tab / kind / subtype / drawing
filters / columns / dimensions / controls / provenance
```

`main.PAGES` 构建时自动填充：

- `group`：标准组；
- `kind`：`page_kind()`；
- `drawing`：`flange:WN`、`fitting:elbow`、`pipe`、`gasket:flat` 等；
- `controls`：`face` / `angle`。

树节点元数据追加 `PageSpec`，`ui.vector_export` 直接读取 `drawing` 字段选择矢量工厂，不再靠模板名猜类型。

## 五、测试

```text
Ran 111 tests
OK
```

新增：

- DrawingSpec 轮廓/尺寸数量；
- PDF 文件头 `%PDF`；
- SVG 文件包含 `<svg`；
- 弯头 spec；
- PageSpec 扩展字段与 4 元组兼容。

## 六、当前边界

1. 矢量 spec 已覆盖法兰、弯头/三通/异径管/管帽、垫片、钢管、波纹管、密封面参考图；
2. 打印预览在支持 spec 的页面已使用矢量绘制，未支持页面回退栅格；
3. 尺寸布局器已用于法兰，但尚未做全图种碰撞回归；
4. PageSpec 已能承载 filters/columns/dimensions，但 `main.py` 的旧配置仍是事实源，后续逐步迁移。

## 七、3.16.3 管件投影校准

- 三通：增加三端坡口、D 尺寸；
- 异径管：增加两端坡口、D1/D2 尺寸；
- 管帽：按 `E`（直边）/`E1`（总长）绘制直边 + 椭圆封头；
- 波纹管：改用 70B125 的圆弧-公切线波形，不再用正弦近似；
- 管件页新增 Sch 选择器：按 `GB12459_GBT13401.csv` 的 DN+Sch 取真实壁厚；\n- 三通增加支管/主管相贯线（外壁实线、内壁虚线）；\n- 未选择 Sch 或表缺值时仍回退示意壁厚。

