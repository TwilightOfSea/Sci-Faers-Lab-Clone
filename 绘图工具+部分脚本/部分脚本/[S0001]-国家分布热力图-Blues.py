import sys
import pandas as pd
import plotly.express as px
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QInputDialog, QMessageBox, QHeaderView, QTextEdit, QDialog,
    QLabel, QLineEdit, QSpinBox
)
from PyQt5.QtCore import Qt

class CountryInputDialog(QDialog):
    """非模态的国家数据输入对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加国家数据")
        self.setGeometry(500, 200, 300, 200)
        self.setModal(False)  # 设置为非模态
        self.country_data = None
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # 国家名称输入
        layout.addWidget(QLabel("国家名称:"))
        self.country_edit = QLineEdit()
        layout.addWidget(self.country_edit)
        
        # 样本数输入
        layout.addWidget(QLabel("样本数:"))
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(0, 999999)
        layout.addWidget(self.count_spinbox)
        
        # ISO代码输入
        layout.addWidget(QLabel("ISO三字代码:"))
        self.iso_edit = QLineEdit()
        self.iso_edit.setMaxLength(3)
        layout.addWidget(self.iso_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("确认")
        cancel_btn = QPushButton("取消")
        
        confirm_btn.clicked.connect(self.confirm)
        cancel_btn.clicked.connect(self.cancel)
        
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def confirm(self):
        country = self.country_edit.text().strip()
        count = self.count_spinbox.value()
        iso = self.iso_edit.text().strip().upper()
        
        if not country:
            QMessageBox.warning(self, '警告', '请输入国家名称')
            return
            
        if len(iso) != 3:
            QMessageBox.warning(self, '警告', '三字母代码必须为3个字符')
            return
            
        self.country_data = {
            'country': country,
            'count': count,
            'iso_alpha': iso
        }
        self.accept()
        
    def cancel(self):
        self.country_data = None
        self.reject()

class CountryCodeDialog(QDialog):
    """非模态的国家代码对应表窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("常见国家代码对应表")
        self.setGeometry(700, 100, 400, 500)
        self.setModal(False)  # 确保为非模态
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # 创建文本框显示国家代码对应表
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        msg = """若有补充请百度搜索对应国家三字代码：

CN - CHN - China - 中国
US - USA - United States - 美国
JP - JPN - Japan - 日本
GB - GBR - United Kingdom - 英国
FR - FRA - France - 法国
DE - DEU - Germany - 德国
RU - RUS - Russia - 俄罗斯
IN - IND - India - 印度
BR - BRA - Brazil - 巴西
CA - CAN - Canada - 加拿大
AU - AUS - Australia - 澳大利亚
KR - KOR - South Korea - 韩国
IT - ITA - Italy - 意大利
ES - ESP - Spain - 西班牙
NL - NLD - Netherlands - 荷兰
CH - CHE - Switzerland - 瑞士
SE - SWE - Sweden - 瑞典
NO - NOR - Norway - 挪威
DK - DNK - Denmark - 丹麦
FI - FIN - Finland - 芬兰
SG - SGP - Singapore - 新加坡
TH - THA - Thailand - 泰国
MY - MYS - Malaysia - 马来西亚
ID - IDN - Indonesia - 印度尼西亚
VN - VNM - Vietnam - 越南"""
        
        text_edit.setPlainText(msg)
        layout.addWidget(text_edit)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

class CountryTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('国家分布热力图绘制')
        self.resize(800, 700)
        
        # 国家代码对应表窗口实例
        self.country_code_dialog = None
        # 国家数据输入对话框实例
        self.country_input_dialog = None

        # 初始数据
        data = {
            'country': ['China', 'United States', 'India', 'Germany', 'Brazil', 'Japan', 'France', 'United Kingdom'],
            'count': [1200, 800, 900, 400, 300, 350, 280, 250],
            'iso_alpha': ['CHN', 'USA', 'IND', 'DEU', 'BRA', 'JPN', 'FRA', 'GBR']
        }
        self.df = pd.DataFrame(data)

        self.initUI()
        self.showTop20Msg()

    def initUI(self):
        layout = QVBoxLayout()

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['国家', '样本数', '三字代码'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.updateTable()
        layout.addWidget(self.table)

        # 按钮区
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加国家数据")
        add_btn.clicked.connect(self.addRow)
        del_btn = QPushButton("删除选中行")
        del_btn.clicked.connect(self.delRow)
        map_btn = QPushButton("生成地图")
        map_btn.clicked.connect(self.showMap)
        # 添加显示国家代码表的按钮
        code_btn = QPushButton("显示国家代码表")
        code_btn.clicked.connect(self.showTop20Msg)

        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(map_btn)
        btn_layout.addWidget(code_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def syncTableToDataFrame(self):
        """将表格中的数据同步到DataFrame"""
        data = []
        for i in range(self.table.rowCount()):
            country_item = self.table.item(i, 0)
            count_item = self.table.item(i, 1)
            iso_item = self.table.item(i, 2)
            
            if country_item and count_item and iso_item:
                try:
                    country = country_item.text().strip()
                    count = int(count_item.text().strip())
                    iso_alpha = iso_item.text().strip()
                    data.append({'country': country, 'count': count, 'iso_alpha': iso_alpha})
                except ValueError:
                    # 如果转换失败，使用原来DataFrame中的数据
                    if i < len(self.df):
                        data.append(self.df.iloc[i].to_dict())
        
        if data:
            self.df = pd.DataFrame(data)

    def updateTable(self):
        self.table.setRowCount(len(self.df))
        for i, row in self.df.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(str(row['country'])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row['count'])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row['iso_alpha'])))

    def addRow(self):
        """使用非模态对话框添加国家数据"""
        if self.country_input_dialog is None:
            self.country_input_dialog = CountryInputDialog(self)
            self.country_input_dialog.accepted.connect(self.onCountryDataConfirmed)
        
        # 清空之前的输入
        self.country_input_dialog.country_edit.clear()
        self.country_input_dialog.count_spinbox.setValue(0)
        self.country_input_dialog.iso_edit.clear()
        
        # 显示非模态对话框
        self.country_input_dialog.show()
        self.country_input_dialog.country_edit.setFocus()

    def onCountryDataConfirmed(self):
        """处理确认的国家数据"""
        if self.country_input_dialog and self.country_input_dialog.country_data:
            data = self.country_input_dialog.country_data
            
            # 先同步表格数据到DataFrame
            self.syncTableToDataFrame()
            
            # 使用pd.concat替代append方法
            new_row = pd.DataFrame([data])
            self.df = pd.concat([self.df, new_row], ignore_index=True)
            self.updateTable()
            
            # 隐藏输入对话框
            self.country_input_dialog.hide()

    def delRow(self):
        selected = self.table.currentRow()
        if selected < 0:
            return
        
        # 先同步表格数据到DataFrame
        self.syncTableToDataFrame()
        
        # 删除指定行
        self.df = self.df.drop(self.df.index[selected]).reset_index(drop=True)
        self.updateTable()

    def showMap(self):
        # 先同步表格数据到DataFrame
        self.syncTableToDataFrame()
        
        # 生成地图
        fig = px.choropleth(
            self.df,
            locations='iso_alpha',
            color='count',
            hover_name='country',
            color_continuous_scale='Blues',
            title='National Distribution Heat Map'
        )
        fig.update_layout(
            title_font_size=16,
            geo=dict(
                showframe=False,
                showcoastlines=True,
            )
        )
        fig.show()

    def showTop20Msg(self):
        """显示非模态的国家代码对应表窗口"""
        if self.country_code_dialog is None:
            self.country_code_dialog = CountryCodeDialog(self)
        
        # 如果窗口已经显示，就将其置于前台
        if self.country_code_dialog.isVisible():
            self.country_code_dialog.raise_()
            self.country_code_dialog.activateWindow()
        else:
            # 显示非模态窗口
            self.country_code_dialog.show()

# 全局变量存储应用实例
app = None
win = None

def plot(data_path, output_path):
    """
    标准的plot函数，用于启动国家分布热力图绘制GUI应用
    """
    global app, win
    
    # 检查是否已经有QApplication实例
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    
    # 创建主窗口
    win = CountryTable()
    win.show()
    
    # 如果是独立运行，则启动事件循环
    if __name__ == '__main__':
        sys.exit(app.exec_())
    else:
        # 如果是被导入使用，不阻塞主线程
        return win

if __name__ == '__main__':
    plot()
