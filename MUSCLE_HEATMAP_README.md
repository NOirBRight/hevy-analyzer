# Muscle Heatmap Feature - 肌肉热力图功能

## 功能概述

在 **Muscle Distribution** 页面中，新增了一个交互式肌肉热力图，可以根据所选的 Metrics（Workouts、Duration、Volume、Sets）直观地展示各个肌肉群的训练强度分布。

## 主要特性

### 1. 双视图人体模型
- **正面视图（Front View）**：显示胸部、肩部前侧、手臂前侧、腹部核心、腿部前侧
- **背面视图（Back View）**：显示背部、肩部后侧、手臂后侧、下背部、腿部后侧和臀部

### 2. 颜色热力映射
根据训练强度，肌肉部位会显示不同颜色：
- 🔵 **蓝色**：低强度训练
- 🟢 **绿色**：中低强度
- 🟡 **黄色**：中等强度
- 🟠 **橙色**：中高强度
- 🔴 **红色**：高强度训练

颜色计算基于当前周期内所有肌肉群的相对训练量，自动归一化显示。

### 3. 交互式图例
- 显示所有六大肌肉群（Chest、Back、Shoulders、Arms、Core、Legs）
- 每个肌肉群显示对应的颜色块和具体数值
- 底部展示完整的强度渐变色标

### 4. 响应式设计
- 桌面端：左右布局，人体模型在左，图例在右
- 移动端：自适应垂直布局

## 技术实现

### 文件结构
```
HevyAnalyzer/
├── app.py                      # 主应用程序
├── muscle_heatmap_svg.html     # SVG 人体热力图组件
├── exercises.csv               # 动作与肌肉群映射表
└── hevy_workouts_sample.csv    # 示例训练数据
```

### 数据流程
1. **数据聚合**：`build_muscle_distribution()` 函数根据选定的 metric 和 period 聚合数据
2. **数据注入**：将聚合后的肌肉数据（JSON 格式）注入到 HTML 模板中
3. **颜色计算**：JavaScript 根据数值范围计算每个肌肉群的颜色
4. **SVG 渲染**：将颜色应用到对应的 SVG 肌肉部位元素上

### 关键代码

#### 1. 在 `render_muscle_distribution()` 中添加热力图
```python
# ---------- 肌肉热力图 ----------
st.markdown("### 🔥 Muscle Training Heatmap")

# 准备当前周期的肌肉数据
muscle_values = {}
for muscle in MUSCLE_GROUPS:
    muscle_row = current_data[current_data["muscle_group"] == muscle]
    if not muscle_row.empty:
        muscle_values[muscle] = float(muscle_row["value"].iloc[0])
    else:
        muscle_values[muscle] = 0.0

# 注入数据到 HTML
muscle_data_json = json.dumps(muscle_values)
html_with_data = html_content.replace("MUSCLE_DATA_PLACEHOLDER", muscle_data_json)

# 渲染组件
components.html(html_with_data, height=600, scrolling=False)
```

#### 2. SVG 人体模型结构
```html
<!-- 胸部示例 -->
<ellipse id="front-chest" class="muscle-part" 
         cx="100" cy="90" rx="28" ry="20" fill="#10B981"/>

<!-- 腿部示例 -->
<ellipse id="front-legs-left" class="muscle-part" 
         cx="85" cy="230" rx="18" ry="70" fill="#EF4444"/>
```

#### 3. 颜色计算算法
```javascript
function getColorByIntensity(value, allData) {
    const values = Object.values(allData).filter(v => v > 0);
    const max = Math.max(...values);
    const min = Math.min(...values);
    const normalized = (value - min) / (max - min || 1);
    
    // 五色渐变映射
    if (normalized < 0.25) return lerpColor('#3B82F6', '#10B981', normalized * 4);
    else if (normalized < 0.5) return lerpColor('#10B981', '#FBBF24', (normalized - 0.25) * 4);
    else if (normalized < 0.75) return lerpColor('#FBBF24', '#F97316', (normalized - 0.5) * 4);
    else return lerpColor('#F97316', '#EF4444', (normalized - 0.75) * 4);
}
```

## 使用方法

1. **启动应用**：
   ```bash
   streamlit run app.py
   ```

2. **上传数据**：
   - 点击侧边栏的数据源管理
   - 上传 `hevy_workouts.csv` 文件
   - 或者使用示例数据 `hevy_workouts_sample.csv`

3. **选择周期**：
   - 在浮动控制栏中选择 Week 或 Month 视图
   - 使用左右箭头切换不同时间段

4. **查看热力图**：
   - 滚动到 "Muscle Distribution" 部分
   - 热力图会根据当前选择的 Metric（Workouts/Duration/Volume/Sets）和时间周期自动更新
   - 悬停在肌肉部位上可以查看详细信息

5. **切换 Metric**：
   - 在顶部选择不同的 Metric
   - 热力图会实时更新颜色分布

## 数据示例

假设当前周期的训练数据：
```json
{
    "Chest": 1500.5,
    "Back": 2200.8,
    "Shoulders": 800.3,
    "Arms": 1200.6,
    "Core": 600.2,
    "Legs": 3000.9
}
```

热力图将显示：
- **Legs** 🔴（最高强度 - 红色）
- **Back** 🟠（次高强度 - 橙色）
- **Chest** 🟡（中等强度 - 黄色）
- **Arms** 🟢（中低强度 - 绿色）
- **Shoulders** 🔵（较低强度 - 蓝色）
- **Core** 🔵（最低强度 - 蓝色）

## 自定义和扩展

### 修改肌肉群映射
在 `exercises.csv` 中调整 `primary_muscle` 和 `other_muscles` 列来改变动作与肌肉群的映射关系。

### 调整颜色方案
修改 `muscle_heatmap_svg.html` 中的渐变色值：
```javascript
// 当前配置
const colors = ['#3B82F6', '#10B981', '#FBBF24', '#F97316', '#EF4444'];

// 可以替换为自定义色系，例如紫色系：
const colors = ['#9333EA', '#A855F7', '#C084FC', '#D8B4FE', '#E9D5FF'];
```

### 添加更多身体部位
在 SVG 中添加新的 `<ellipse>` 或 `<rect>` 元素，并在 `muscleMapping` 对象中添加对应的 ID 映射。

## 注意事项

1. **数据完整性**：确保 `exercises.csv` 包含所有训练动作的肌肉群映射
2. **浏览器兼容性**：建议使用 Chrome、Firefox、Safari 或 Edge 最新版本
3. **性能优化**：对于大数据集，颜色计算是实时进行的，性能表现良好
4. **单位一致性**：热力图数值会根据用户设置的单位（KG/LBS）自动转换

## 未来改进方向

- [ ] 添加 3D 旋转动画效果
- [ ] 支持更细粒度的肌肉部位（如二头肌/三头肌分离显示）
- [ ] 添加时间轴播放功能，查看肌肉强度随时间的变化
- [ ] 导出热力图为图片功能
- [ ] 添加肌肉群对比模式（对比两个不同周期）

## 技术栈

- **前端**：HTML5 SVG、原生 JavaScript、CSS3
- **后端**：Python 3.11、Streamlit
- **数据处理**：Pandas、NumPy
- **可视化**：Plotly（其他图表）、自定义 SVG（热力图）

## 许可证

此功能是 HevyAnalyzer 项目的一部分，遵循项目的整体许可证。
