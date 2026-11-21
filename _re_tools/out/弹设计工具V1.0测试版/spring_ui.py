# Reconstructed from bytecode by split_decompile.py
# spring_ui.pyc

'''弹簧设计工具主界面（精简设计工具三前提：参数+结果同页、次要折叠、无绝对化词）。'''
import os
import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QFileDialog, QDoubleSpinBox, QGroupBox, QGridLayout, QMessageBox, QDialog
from PySide6.QtGui import QIcon
import spring_data as SD
import spring_calc as SC
import spring3d as S3
import theme

def glyph_icon(kind, size):
    return QIcon()
class MainWindow:

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f'''弹簧设计工具 {SD.VERSION}''')
        self.setMinimumSize(920, 680)
        self._geom = None
        self._result_lines = None
        self._result_title = '校核结果'
        theme.init_from_config()
        self._setup_style()
        self._build_ui()
    def _setup_style(self):
        self.setStyleSheet(theme.qss())
        if hasattr(self, 'hint'):
            self._refresh_inline_styles()
            return None
    def _refresh_inline_styles(self):
        '''换肤时刷新那些写在控件上的内联颜色（结果区、提示行）。'''
        t = theme.current()
        self.result_text.setStyleSheet(f'''color: {t['text2']}; font-size: 13px;''')
        self.export_hint.setStyleSheet(f'''color: {t['text2']}; font-size: 11px;''')
        self.hint.setStyleSheet(f'''color: {t['text2']}; font-size: 11px; padding: 8px; background: {t['card']}; border-radius: {t['radius']};''')
        self.result_card.setStyleSheet(f'''QGroupBox {{ background: {t['card']}; border: 1px solid {t['border']}; border-left: 3px solid {t['accent']}; border-radius: {t['radius']}; margin-top: 12px; padding-top: 12px; }}QGroupBox::title {{ subcontrol-origin: margin; left: 12px; padding: 0 6px; color: {t['text2']}; font-weight: bold; }}''')
    def apply_theme(self, name):
        '''切换主题：重设样式 + 用新 token 重渲染已有结果。'''
        if not theme.set_theme(name):
            return False
        None._setup_style()
        if self._result_lines:
            self._render_result()
        return True
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setSpacing(16)
        root.setContentsMargins(20, 16, 20, 16)
        left = QVBoxLayout()
        left.setSpacing(12)
        type_row = QHBoxLayout()
        type_row.addWidget(QLabel('弹簧类型：'))
        self.type_cb = QComboBox()
        self.type_cb.addItems([
            '压缩弹簧',
            '拉伸弹簧',
            '扭转弹簧'])
        self.type_cb.currentIndexChanged.connect(self._on_type_changed)
        type_row.addWidget(self.type_cb)
        type_row.addStretch()
        theme_btn = QPushButton('外观')
        theme_btn.setToolTip('切换界面配色（不影响计算与数据）')
        theme_btn.clicked.connect(self._open_theme_dialog)
        type_row.addWidget(theme_btn)
        left.addLayout(type_row)
        param_gb = QGroupBox('基本参数')
        param_grid = QGridLayout(param_gb)
        param_grid.setSpacing(10)
        param_grid.setColumnStretch(1, 1)
        self.inputs = { }
        self.labels = { }

        def add_labeled(row, label, widget, name):
            lbl = QLabel(label)
            if name:
                self.labels[name] = lbl
            param_grid.addWidget(lbl, row, 0)
            param_grid.addWidget(widget, row, 1)
        self.material_cb = QComboBox()
        for m in SD.MATERIALS:
            self.material_cb.addItem(m['name'], m['key'])
            add_labeled(0, '材料：', self.material_cb)
            self.load_cb = QComboBox()
            self.load_cb.addItems([
                '静负荷',
                '有限疲劳寿命',
                '无限疲劳寿命'])
            add_labeled(1, '负荷类型：', self.load_cb)
            self.F2_input = QDoubleSpinBox()
            self.F2_input.setRange(0.1, 1e+07)
            self.F2_input.setDecimals(2)
            self.F2_input.setValue(500)
            add_labeled(2, '最大工作负荷 F2 (N)：', self.F2_input, 'F2')
            self.F1_input = QDoubleSpinBox()
            self.F1_input.setRange(0, 1e+07)
            self.F1_input.setDecimals(2)
            self.F1_input.setValue(100)
            add_labeled(3, '最小工作负荷 F1 (N)：', self.F1_input, 'F1')
            self.stroke_input = QDoubleSpinBox()
            self.stroke_input.setRange(0.1, 5000)
            self.stroke_input.setDecimals(2)
            self.stroke_input.setValue(20)
            add_labeled(4, '工作行程 h (mm)：', self.stroke_input, 'stroke')
            self.M2_input = QDoubleSpinBox()
            self.M2_input.setRange(0.1, 1e+09)
            self.M2_input.setDecimals(2)
            self.M2_input.setValue(5000)
            self.M2_label = QLabel('最大扭矩 M2 (N·mm)：')
            self.labels['M2'] = self.M2_label
            self.M1_input = QDoubleSpinBox()
            self.M1_input.setRange(0, 1e+09)
            self.M1_input.setDecimals(2)
            self.M1_input.setValue(0)
            self.M1_label = QLabel('最小扭矩 M1 (N·mm)：')
            self.labels['M1'] = self.M1_label
            self.angle_input = QDoubleSpinBox()
            self.angle_input.setRange(0.1, 3600)
            self.angle_input.setDecimals(2)
            self.angle_input.setValue(90)
            self.angle_label = QLabel('工作扭转角 φ (°)：')
            self.labels['angle'] = self.angle_label
            param_grid.addWidget(self.M2_label, 5, 0)
            param_grid.addWidget(self.M2_input, 5, 1)
            param_grid.addWidget(self.M1_label, 6, 0)
            param_grid.addWidget(self.M1_input, 6, 1)
            param_grid.addWidget(self.angle_label, 7, 0)
            param_grid.addWidget(self.angle_input, 7, 1)
            left.addWidget(param_gb)
            opt_gb = QGroupBox('更改参数（可选）')
            opt_grid = QGridLayout(opt_gb)
            self.C_input = QDoubleSpinBox()
            self.C_input.setRange(0, 1000)
            self.C_input.setDecimals(2)
            self.C_input.setSpecialValueText('自动推荐')
            self.C_input.setValue(0)
            opt_grid.addWidget(QLabel('旋绕比 C：'), 0, 0)
            opt_grid.addWidget(self.C_input, 0, 1)
            self.Dmax_input = QDoubleSpinBox()
            self.Dmax_input.setRange(0, 5000)
            self.Dmax_input.setDecimals(2)
            self.Dmax_input.setSpecialValueText('不限')
            self.Dmax_input.setValue(0)
            opt_grid.addWidget(QLabel('最大外径 Dmax (mm)：'), 1, 0)
            opt_grid.addWidget(self.Dmax_input, 1, 1)
            left.addWidget(opt_gb)
            calc_btn = QPushButton('开始设计校核')
            calc_btn.clicked.connect(self._calculate)
            left.addWidget(calc_btn)
            left.addStretch()
            right = QVBoxLayout()
            right.setSpacing(12)
            self.result_card = QGroupBox('校核结果')
            self.result_layout = QVBoxLayout(self.result_card)
            self.result_layout.setSpacing(8)
            self.result_text = QLabel('计算后显示结果')
            self.result_text.setWordWrap(True)
            self.result_layout.addWidget(self.result_text)
            right.addWidget(self.result_card)
            self.export_btn = QPushButton('导出三维模型')
            self.export_btn.setEnabled(False)
            self.export_btn.clicked.connect(self._export_3d)
            self.export_hint = QLabel('按当前校核结果生成三维：STEP 为光滑曲面实体（非参数化特征），STL 为刻面网格（STL 格式本身只支持三角面）。')
            self.export_hint.setWordWrap(True)
            right.addWidget(self.export_btn)
            right.addWidget(self.export_hint)
            self.hint = QLabel('提示：本工具按 GB/T 23935-2009 推荐公式估算，动负荷与疲劳结果为近似值；重要场合请以材料标准现行有效版本复核。')
            self.hint.setWordWrap(True)
            right.addWidget(self.hint)
            right.addStretch()
            root.addLayout(left, 1)
            root.addLayout(right, 1)
            self._on_type_changed()
            self._refresh_inline_styles()
            self._result_ready = False
            self._bind_stale_signals()
            return None
    def _on_type_changed(self):
        is_torsion = self.type_cb.currentText() == '扭转弹簧'
        for n in ('F2', 'F1', 'stroke'):
            self.labels[n].setVisible(not is_torsion)
            for n in ('M2', 'M1', 'angle'):
                self.labels[n].setVisible(is_torsion)
                self.F2_input.setVisible(not is_torsion)
                self.F1_input.setVisible(not is_torsion)
                self.stroke_input.setVisible(not is_torsion)
                self.M2_input.setVisible(is_torsion)
                self.M1_input.setVisible(is_torsion)
                self.angle_input.setVisible(is_torsion)
                self.result_card.setTitle('校核结果')
                return None
    def _mark_stale(self, *_a):
        '''任一参数被改动 → 旧结果失效，需重新计算。'''
        if getattr(self, '_result_ready', False):
            self._result_ready = False
            self._geom = None
            self.export_btn.setEnabled(False)
            self._set_result('校核结果（待重算）', [
                ('warn', '参数已修改，上次结果不再对应当前参数，请点击「开始设计校核」重新计算。')])
            return None
    def _set_result(self, title, lines):
        """保存结构化结果行（kind: ''/dim/warn/bad/concl），供换肤时重渲染。"""
        self._result_title = title
        self._result_lines = lines
        self._render_result()
    def _render_result(self):
        '''按当前主题 token 渲染结果文本（换肤后颜色不会残留旧值）。'''
        if not self._result_lines:
            return None
        t = None.current()
        out = []
        for item in self._result_lines:
            text = item[1]
            kind = item[0]
            if kind == 'concl':
                value = item[2] if len(item) > 2 else ''
                v = float(value)
            else:
                except (TypeError, ValueError):
                    v = None
                if v is None and v < 1:
                    col = t['red']
                elif v is None and v < 1.2:
                    col = t['orange']
                else:
                    col = t['accent']
            out.append(f'''<span style=\'font-size:14px\'><b>校核结论：</b>{text} S = <b style=\'color:{col}; font-size:16px\'>{value}</b></span>''')
            if kind == 'dim':
                out.append(f'''<span style=\'color:{t['text2']}\'>{text}</span>''')
                continue
            if kind == 'warn':
                out.append(f'''<span style=\'color:{t['orange']}\'>{text}</span>''')
                continue
            if kind == 'bad':
                out.append(f'''<span style=\'color:{t['red']}\'>{text}</span>''')
                continue
            out.append(text)
            self.result_card.setTitle(self._result_title)
            self.result_text.setText('<br>'.join(out))
            return None
    def _open_theme_dialog(self):
        theme.ThemeDialog(self).exec()
    def _bind_stale_signals(self):
        '''把全部输入控件的变更接到失效标记上，并补充量纲提示。'''
        tips = {
            'F2_input': '最大工作负荷 F2，单位 N（应 ≥ F1）',
            'F1_input': '最小工作负荷 F1，单位 N（可填 0，应 ≤ F2）',
            'stroke_input': '工作行程 h = f2 - f1，单位 mm（应 > 0）',
            'M2_input': '最大工作扭矩 M2，单位 N·mm（应 ≥ M1）',
            'M1_input': '最小工作扭矩 M1，单位 N·mm（可填 0）',
            'angle_input': '工作扭转角 φ，单位 °（应 > 0）',
            'C_input': '旋绕比 C = D/d，留 0 由工具按推荐取值',
            'Dmax_input': '允许最大外径，单位 mm，留 0 表示不限' }
        for name in tips:
            w = getattr(self, name, None)
            if not w is not None:
                continue
            w.setToolTip(tips[name])
            w.valueChanged.connect(self._mark_stale)
            for c in (self.type_cb, self.material_cb, self.load_cb):
                c.currentTextChanged.connect(self._mark_stale)
                return None
    def _reject(self, msg):
        '''输入不合格：弹提示 + 结果区明确未出结论。'''
        self._result_ready = False
        self._geom = None
        self.export_btn.setEnabled(False)
        self._set_result('校核结果（未出结论）', [
            ('bad', f'''输入未通过校验，未给出校核结论：{msg}'''),
            ('dim', '请修正参数后重新计算。')])
        QMessageBox.warning(self, f'''弹簧设计工具 {SD.VERSION}''', f'''输入未通过校验：\n{msg}''')
    _fmt_allow = (lambda r, sym_allow, sym_max: pass)()

    def _calculate(self):

        try:
            key = self.material_cb.currentData()
            material = SD.get_material(key)
            load_text = self.load_cb.currentText()
            load_type = {
                '静负荷': 'static',
                '有限疲劳寿命': 'finite',
                '无限疲劳寿命': 'infinite' }[load_text]
            C_user = self.C_input.value() if self.C_input.value() > 0 else None
            Dmax = self.Dmax_input.value() if self.Dmax_input.value() > 0 else None
            kind = self.type_cb.currentText()
            if kind in ('压缩弹簧', '拉伸弹簧'):
                fn = SC.design_compression if kind == '压缩弹簧' else SC.design_tension
                r = fn(F2 = self.F2_input.value(), F1 = self.F1_input.value(), stroke = self.stroke_input.value(), material = material, load_type = load_type, C_user = C_user, Dmax = Dmax)
                head = '切应力安全系数'
                lines = [
                    ('concl', head, f'''{r['safety']:.2f}'''),
                    ('', f'''材料直径 d = {r['d']:.2f} mm（{material['std']} {material['group']}）'''),
                    ('', f'''中径 D = {r['D']:.2f} mm，旋绕比 C = {r['C']:.2f}'''),
                    ('', f'''有效圈数 n = {r['n']:.1f}（总圈数约 {r['n1']:.1f}）''' if kind == '压缩弹簧' else f'''有效圈数 n = {r['n']:.1f}'''),
                    ('', f'''弹簧刚度 F\' = {r['k']:.3f} N/mm，自由高度 H0 ≈ {r['H0']:.2f} mm''' if kind == '压缩弹簧' else f'''弹簧刚度 F\' = {r['k']:.3f} N/mm，自由长度 ≈ {r['H0']:.2f} mm（{r['H0_note']}）'''),
                    ('', self._fmt_allow(r, '[τ]', 'τmax'))]
                if kind == '压缩弹簧':
                    lines.append(('', f'''节距 t = {r['pitch']:.2f} mm（余隙 δ1 = {r['clearance']:.2f}），压并高度 ≈ {r['Hb']:.2f} mm，可压缩量 {r['f_max']:.2f} mm'''))
                    lines.append(('dim', r['end_type_note']))
                    act = (r['F2'] - r['F1']) / r['k']
                    want = r['stroke']
                    if abs(act - want) / want > 0.02:
                        lines.append(('warn', f'''圈数取整后实际可达行程 {act:.2f} mm（需求 {want:.2f} mm，偏差 {100 * (act - want) / want:+.1f}%）。'''))
                if kind == '拉伸弹簧':
                    lines.append(('dim', r['tension_note']))
                else:
                    r = SC.design_torsion(M2 = self.M2_input.value(), M1 = self.M1_input.value(), angle = self.angle_input.value(), material = material, load_type = load_type, C_user = C_user, Dmax = Dmax)
                    lines = [
                        ('concl', '弯曲应力安全系数', f'''{r['safety']:.2f}'''),
                        ('', f'''材料直径 d = {r['d']:.2f} mm（{material['std']} {material['group']}）'''),
                        ('', f'''中径 D = {r['D']:.2f} mm，旋绕比 C = {r['C']:.2f}'''),
                        ('', f'''有效圈数 n = {r['n']:.1f}，实际扭转角 {r['angle_actual']:.2f}°（需求 {r['angle']:.2f}°）'''),
                        ('', f'''实际扭转刚度 {r['k_torque_actual']:.3f} N·mm/°，{r['angle_note']}'''),
                        ('', self._fmt_allow(r, '[σ]', 'σmax')),
                        ('dim', f'''试验扭矩 Ts ≈ {r['Ts']:.0f} N·mm（试验弯曲应力 σs 查表4），对应变形角 φs ≈ {r['phi_s']:.1f}°''')]
                    lines.append(('dim', r['arm_note']))
            if r.get('fatigue_note'):
                lines.append(('warn', r['fatigue_note']))
            elif not r.get('fatigue_safety') is None:
                if not r.get('tau_u0') is None:
                    verdict = '已满足' if r['fatigue_safety'] >= r['S_min'] else '未满足'
                    lines.append(('', f'''疲劳安全系数 Sf = {r['fatigue_safety']:.2f} = (τu0 {r['tau_u0']:.1f} + 0.75×τmin {r['tau_min']:.1f}) / τmax {r['tau_max']:.1f}'''))
                    lines.append(('', f'''疲劳校核：Smin = {r['S_min']:.1f}，本次{verdict}'''))
                elif 'tau_amp' in r:
                    pass

                amp_key = 'sigma_amp'
                base_key = 'sigma_allow_amp' if 'sigma_allow_amp' in r else 'tau_allow_amp'
                lines.append(('', f'''疲劳安全系数 Sf = {r['fatigue_safety']:.2f}（= {r.get(base_key, 0):.1f} / {r.get(amp_key, 0):.1f}）'''))
                lines.append(('dim', r['fatigue_basis']))
            if r.get('stability_note'):
                lines.append(('warn', r['stability_note']))
            if r.get('c_note'):
                lines.append(('warn', r['c_note']))
            for g in r.get('geometry_notes', []):
                lines.append(('warn', g))
                for g in r.get('ts_notes', []):
                    lines.append(('warn', g))
                    for w in r.get('warnings', []):
                        lines.append(('bad', w))
                        if r['safety'] < 1:
                            lines.append(('bad', '注意：安全系数小于1，当前参数下强度未通过校核。'))
                            lines.append(('dim', '可考虑减小旋绕比 C、放宽外径约束或更换强度更高的材料，再重新校核。'))
                        elif r['safety'] < 1.2:
                            lines.append(('warn', '安全系数裕度偏小，可按工况与材料批次另行确认。'))
            lines.append(('dim', f'''许用应力取值：{r['allow_basis']}；G = {r['G'] / 1000:.1f} GPa，E = {r['E'] / 1000:.1f} GPa。'''))
            self._set_result('校核结果', lines)
            self._result_ready = True
            if kind == '压缩弹簧':
                self._geom = dict(d = r['d'], D = r['D'], n = r['n'], H0 = r['H0'], nt = r['n1'])
                self.export_btn.setEnabled(True)
                self.export_hint.setText('可导出压缩弹簧三维模型（STEP 为刻面逼近，非参数化特征）。')
                return None
            self._geom = 'tau_amp'
            self.export_btn.setEnabled(False)
            self.export_hint.setText('拉伸/扭转弹簧的三维生成暂未开放。')
            return None
        except SC.InputError:
            e = None
            self._reject(str(e))
            e = None
            del e
            return None
            e = None
            del e
            except Exception:
                e = None
                self._result_ready = False
                self._geom = None
                self.export_btn.setEnabled(False)
                self._set_result('校核结果（未出结论）', [
                    ('bad', f'''本次未给出校核结论，计算过程报错：{e}''')])
                QMessageBox.critical(self, f'''弹簧设计工具 {SD.VERSION}''', f'''计算出错：{e}''')
                e = None
                del e
                return None
                e = None
                del e
    def _export_3d(self):
        g = getattr(self, '_geom', None)
        if not g:
            QMessageBox.information(self, f'''弹簧设计工具 {SD.VERSION}''', '请先在压缩弹簧下完成一次设计校核。')
            return None
        default_name = f'''{None}{g['d']:.2f}_D{g['D']:.2f}_H{g['H0']:.1f}.stp'''
        (path, _sel) = QFileDialog.getSaveFileName(self, '导出三维模型', default_name, 'STEP 模型 (*.stp);;STL 模型 (*.stl)')
        if not path:
            return None

        try:
            st = S3.export(path, g['d'], g['D'], g['n'], g['H0'], nt = g['nt'])
        except ValueError:
            e = None
            QMessageBox.warning(self, f'''弹簧设计工具 {SD.VERSION}''', f'''未能生成三维模型：{e}''')
            e = None
            del e
            return None
            e = None
            del e
            except Exception:
                e = None
                QMessageBox.warning(self, f'''弹簧设计工具 {SD.VERSION}''', f'''导出出错：{e}''')
                e = None
                del e
                return None
                e = None
                del e

        size_kb = st['file_size'] // 1024
        if st.get('mode') == 'smooth':
            (lo, hi) = st.get('bbox_ctrl', ((0, 0, 0), (0, 0, 0)))
            over = max(abs(hi[0]), abs(hi[1]), abs(lo[0]), abs(lo[1])) - (g['D'] + g['d']) / 2
            tail = f'''\n量尺寸提示：CAD 的「包围盒」按控制点网算（UG/NX 实测如此），外径读数会比真实大约 {2 * over:.2f} mm，量尺寸请以曲面为准。''' if over > 0.01 else ''
            QMessageBox.information(self, '三维模型已导出', f'''文件：{path}\n光滑曲面实体：{st['faces']} 张面（管身 {st['faces'] - 2} 张 B 样条曲面 + 2 张端封盖），文件大小约 {size_kb} KB\n导入 CAD 后是曲面实体，不是三角面片。\n说明：螺旋线为超越曲线，无法用多项式精确表示，这里的曲面到理论螺旋管面的偏差实测在线径的 0.5% 以内。''' + tail)
            return None
        why = None.get('fallback')
        tail = f'''\n光滑曲面未能生成，已退回刻面实体（{why}）''' if why else ''
        QMessageBox.information(self, '三维模型已导出', f'''文件：{path}\n网格：{st['faces']} 面 / {st['vertices']} 顶点，流形自检{'通过' if st['manifold'] else '未通过'}\n体积：{st['volume']:.0f} mm³，文件大小约 {size_kb} KB\n说明：圆截面按 16 边形、螺旋线每圈 48 段逼近，属刻面实体；导入 CAD 后建议核对几何尺寸（刻面实体，非参数化）。{tail}''')
    __classcell__ = staticmethod
    return staticmethod
def _crash_log_path():
    if not os.environ.get('SPRINGTOOL_HOME'):
        pass
    base = os.path.join(os.path.expanduser('~'), '.SpringTool')
    return os.path.join(base, 'crash.log')
def _write_crash_log(err):

    try:
        path = _crash_log_path()
        os.makedirs(os.path.dirname(path), exist_ok = True)
        f = open(path, 'w', encoding = 'utf-8')
        f.write(err)

        try:
            None(None, None)
        with None:
            if not None:

                try:

                    try:
                        return path
                    except OSError:
                        print(err, file = sys.stderr)
                        return None
def main():
    import ctypes

    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            sys.exit(0)
        else:
            except Exception:
                pass

            try:
                app = QApplication(sys.argv)
                theme.init_from_config()
                if type(app).__name__ == 'QApplication':
                    QPalette = QPalette
                    QColor = QColor
                    import PySide6.QtGui
                    t = theme.current()
                    p = QPalette()
                    p.setColor(QPalette.ColorRole.Window, QColor(t['bg']))
                    p.setColor(QPalette.ColorRole.WindowText, QColor(t['text']))
                    p.setColor(QPalette.ColorRole.Base, QColor(t['card']))
                    p.setColor(QPalette.ColorRole.Text, QColor(t['text']))
                    p.setColor(QPalette.ColorRole.Button, QColor(t['card']))
                    p.setColor(QPalette.ColorRole.ButtonText, QColor(t['text']))
                    app.setPalette(p)
                app.setWindowIcon(glyph_icon('spring'))
                import dialogs
                if dialogs.is_first_run():
                    welcome = dialogs.WelcomeDialog()
                    if welcome.exec() != QDialog.Accepted:
                        sys.exit(0)
                    cfg = dialogs.load_config()
                    cfg['first_run'] = False
                    dialogs.save_config(cfg)
                if not dialogs.is_unlocked():
                    lock = dialogs.LockDialog()
                    if lock.exec() != QDialog.Accepted:
                        sys.exit(0)
                if not dialogs.is_disclaimer_accepted():
                    disc = dialogs.DisclaimerDialog()
                    if disc.exec() != QDialog.Accepted:
                        sys.exit(0)
                win = MainWindow()
                win.show()
                sys.exit(app.exec())
                return None
            except SystemExit:
                raise 
                except Exception:
                    import traceback
                    err = traceback.format_exc()
                    _write_crash_log(err)
                    QMessageBox.critical(None, f'''弹簧设计工具 {SD.VERSION} — 启动失败''', f'''请将以下信息发给开发者：\n\n{err[-1000:]}''')
                    return None
                    except Exception:
                        return None
if __name__ == '__main__':
    main()
    return None
