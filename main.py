from ultralytics import YOLO

# ==================== 杂草分类模型（EfficientNetV2）====================
model = YOLO("efficientnetv2s-cls.pt")  # 自动下载，不会报错

# 测试一张图片
result = model("test.png")
result.show()  # 展示结果