import sys
import random
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QMenu
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtCore import QPointF
from PyQt6.QtWidgets import QInputDialog
from PyQt6.QtCore import QEvent

# 导入api_request.py
from chatgpt import get_response

def distance_between_points(p1, p2):
    return ((p1.x() - p2.x())**2 + (p1.y() - p2.y())**2)**0.5

def normalize_point(point):
    length = (point.x()**2 + point.y()**2)**0.5
    if length == 0:
        return QPointF(0, 0)
    return QPointF(point.x()/length, point.y()/length)


class DesktopPet(QMainWindow):
    def __init__(self):
        super().__init__()

        self.is_moving = True
        self.target_position = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.set_random_target)

        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.step_move)

        self.initUI()

        self.actions = [
            ['1', '2', '3'],
            ['4', '5', '6', '7', '8', '9', '10', '11'],
            ['12', '13', '14'],
            ['15', '16', '17'],
            ['18', '19'],
            ['20', '21'],
            ['22'],
            ['23', '24', '25'],
            ['26', '27', '28', '29'],
            ['30', '31', '32', '33'],
            ['34', '35', '36', '37'],
            ['38', '39', '40', '41'],
            ['42', '43', '44', '45', '46']
        ]

        self.current_action_index = 0
        self.current_image_index = 0

        self.conversation_id = None
        self.parent_message_id = None

        # 每5秒更改动作
        self.action_timer = QTimer(self)
        self.action_timer.timeout.connect(self.change_action)
        self.action_timer.start(5000)  # 设置为5秒，您可以根据需要调整

        # 每0.2秒更改图像模拟动作
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.animate_action)
        self.animation_timer.start(200)  # 设置为0.2秒，您可以根据需要调整

        # 气泡的初始化
        self.bubble_label = QLabel(self)
        self.bubble_label.setWordWrap(True)
        self.bubble_label.setStyleSheet("background-color: white; border-radius: 10px; padding: 5px; border: 1px solid black;")
        self.bubble_label.hide()

        self.bubble_timer = QTimer(self)
        self.bubble_timer.timeout.connect(self.hide_bubble)

    def change_action(self):
        # 随机选择一个新的动作，确保新的动作与当前的动作不同
        new_action_index = random.choice([i for i in range(len(self.actions)) if i != self.current_action_index])
        self.current_action_index = new_action_index
        self.current_image_index = 0

        # 设置下次切换动作的随机时间（这里设置为5到10秒，您可以根据需要调整）
        self.action_timer.start(random.randint(5000, 10000))

    def animate_action(self):
        # 清除当前图像
        self.pet_image.clear()

        # 获取当前动作的图片列表并设置新图像
        current_action = self.actions[self.current_action_index]
        pixmap = QPixmap(f"pikachu/shime{current_action[self.current_image_index]}.png")

        # 直接设置Pixmap，不进行缩放
        self.pet_image.setPixmap(pixmap)

        # 更新当前图像索引
        self.current_image_index = (self.current_image_index + 1) % len(current_action)

    def initUI(self):
        # 设置窗口透明度、无边框并确保其始终在顶部
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)

        # # 加载并显示宠物图片，并进行缩放
        self.pet_image = QLabel(self)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.pet_image)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.show()

        # 固定窗口大小
        # 获取屏幕的设备像素比率
        ratio = self.window().screen().devicePixelRatio()
        # 将逻辑像素转换为物理像素
        logical_width = 100 * ratio
        logical_height = 100 * ratio
        # 使用逻辑像素设置固定大小
        self.setFixedSize(int(logical_width), int(logical_height))

        # self.setFixedSize(200,200)

        # 设置初始位置为随机位置
        self.random_position()

        # 开始QTimer
        self.timer.start(random.randint(100000, 200000))  # 每100-200秒移动一次

    def set_random_target(self):
        if not self.is_moving:
            return

        screen_geometry = QApplication.primaryScreen().geometry()
        target_x = random.randint(0, screen_geometry.width() - 250)
        target_y = random.randint(0, screen_geometry.height() - 150)
        self.target_position = QPoint(target_x, target_y)

        # 根据距离来调整移动计时器的速度
        distance = distance_between_points(self.pos(), self.target_position)
        interval = max(10, int(distance / 200))
        self.move_timer.start(interval)

    def step_move(self):
        if not self.target_position:
            return

        current_position = self.pos()
        diff = self.target_position - current_position
        direction = normalize_point(diff)
        step_float = direction * 5
        step = QPoint(int(step_float.x()), int(step_float.y()))

        new_position = current_position + step
        self.move(new_position)

        # 如果到达目标，停止移动计时器
        if distance_between_points(current_position, self.target_position) < 5:
            self.move_timer.stop()

    def random_move(self):
        if not self.is_moving:
            return

        dx = random.randint(-100, 100)  # 增加移动距离
        dy = random.randint(-100, 100)

        new_x = max(min(self.x() + dx, QApplication.primaryScreen().geometry().width() - 250), 0)
        new_y = max(min(self.y() + dy, QApplication.primaryScreen().geometry().height() - 150), 0)

        self.move(new_x, new_y)

    def random_position(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = random.randint(0, screen_geometry.width() - 250)
        y = random.randint(0, screen_geometry.height() - 150)
        self.move(x, y)


    def contextMenuEvent(self, event):
        context_menu = QMenu()
        toggle_move_action = QAction("开启/停止移动", self)
        toggle_move_action.triggered.connect(self.toggle_movement)
        context_menu.addAction(toggle_move_action)

        exit_action = context_menu.addAction("退出")
        exit_action.triggered.connect(self.close)

        context_menu.exec(event.globalPos())

    def toggle_movement(self):
        self.is_moving = not self.is_moving
        if self.is_moving:
            self.timer.start(random.randint(100000, 200000))
        else:
            self.timer.stop()
            self.move_timer.stop()

    # 重写鼠标拖动事件，使窗口可以被拖动
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.dragPosition)
            event.accept()

    def mousePressEvent(self, event):
        if event.type() == QEvent.Type.MouseButtonDblClick:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查鼠标位置是否在宠物图像的范围内
            if self.pet_image.geometry().contains(event.pos()):
                self.dragPosition = event.globalPosition().toPoint() - self.geometry().topLeft()
                event.accept()

    def show_bubble(self, text, duration=5000):  # 显示5秒
        # 设置文本
        self.bubble_label.setText(text)
        self.bubble_label.adjustSize()

        self.bubble_label.move(0,0)
        self.bubble_label.show()

        # 设置定时器来隐藏气泡
        self.bubble_timer.start(duration)

    def hide_bubble(self):
        self.bubble_label.setHidden(True)
        self.bubble_label.hide()
        self.bubble_label.setText(None)

    def mouseDoubleClickEvent(self, event):
        text, ok = QInputDialog.getText(self, '与宠物交谈', '请输入您的问题：')

        if ok and text.strip():
            # 调用get_response函数
            json_response = get_response(text, self.conversation_id, self.parent_message_id)

            # 从响应中更新conversation_id和parent_message_id
            self.conversation_id = json_response["conversation_id"]
            self.parent_message_id = json_response["message"]["metadata"]["parent_id"]

            # 获取回答
            answer = ' '.join(json_response["message"]["content"]["parts"])

            print(answer)

            # 显示回答在对话气泡中
            # QMessageBox.information(self, '宠物回答', answer)
            self.show_bubble(answer)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = DesktopPet()
    sys.exit(app.exec())
