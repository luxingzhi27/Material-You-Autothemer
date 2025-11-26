import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import org.kde.plasma.components 3.0 as PlasmaComponents
import org.kde.plasma.extras as PlasmaExtras
import org.kde.kirigami as Kirigami

Item {
    id: root

    // 1. 核心修复：明确告诉 Plasma 这个弹窗有多大
    // 使用 Kirigami 单位确保在 4K 屏上也不会太小
    implicitWidth: Kirigami.Units.gridUnit * 22
    implicitHeight: Kirigami.Units.gridUnit * 28

    // 接收配置对象
    property var settings: null

    // 2. 使用 Representation 获取标准背景和头部
    PlasmaExtras.Representation {
        anchors.fill: parent
        collapseMarginsHint: true // 让标题栏贴顶

        // 标题栏
        header: PlasmaExtras.PlasmoidHeading {
            contentItem: RowLayout {
                PlasmaExtras.Heading {
                    text: "Matugen Theme"
                    level: 1
                    Layout.fillWidth: true
                }
                // 右上角设置图标（可选）
                PlasmaComponents.ToolButton {
                    icon.name: "configure"
                    text: "Configure"
                    visible: false // 暂时隐藏，有需要可开启
                }
            }
        }

        // 内容区域
        contentItem: ScrollView {
            id: scrollView
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            // 3. 主布局容器
            ColumnLayout {
                width: scrollView.availableWidth
                spacing: 0 // 间距由内部元素控制

                // --- 区块：Appearance (明暗模式) ---
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.smallSpacing

                    PlasmaExtras.Heading {
                        level: 3
                        text: "Appearance"
                        opacity: 0.7
                    }

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: Kirigami.Units.largeSpacing

                        // Light Mode
                        PlasmaComponents.Button {
                            text: "Light"
                            icon.name: "weather-clear"
                            Layout.fillWidth: true
                            checkable: true
                            // 安全读取配置
                            checked: (root.settings?.colorMode || "dark") === "light"
                            onClicked: if(root.settings) root.settings.colorMode = "light"
                        }

                        // Dark Mode
                        PlasmaComponents.Button {
                            text: "Dark"
                            icon.name: "weather-clear-night"
                            Layout.fillWidth: true
                            checkable: true
                            checked: (root.settings?.colorMode || "dark") === "dark"
                            onClicked: if(root.settings) root.settings.colorMode = "dark"
                        }
                    }
                }

                // --- 分割线 (参考 kde-material-you-colors) ---
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: Kirigami.Theme.textColor
                    opacity: 0.1
                    Layout.topMargin: Kirigami.Units.mediumSpacing
                    Layout.bottomMargin: Kirigami.Units.mediumSpacing
                }

                // --- 区块：Flavor (配色风格) ---
                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.smallSpacing

                    PlasmaExtras.Heading {
                        level: 3
                        text: "Color Flavor"
                        opacity: 0.7
                    }

                    // 风格说明文本
                    PlasmaComponents.Label {
                        text: "Select the algorithm used to generate colors."
                        font: Kirigami.Theme.smallFont
                        opacity: 0.6
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }

                    // 网格布局展示风格
                    GridLayout {
                        columns: 2
                        rowSpacing: Kirigami.Units.smallSpacing
                        columnSpacing: Kirigami.Units.smallSpacing
                        Layout.fillWidth: true

                        Repeater {
                            model: [
                                "tonal-spot", "vibrant", "expressive", "fruit-salad",
                                "content", "neutral", "rainbow", "fidelity"
                            ]

                            delegate: PlasmaComponents.Button {
                                // 首字母大写处理
                                text: modelData.replace("-", " ").replace(/\b\w/g, c => c.toUpperCase())
                                Layout.fillWidth: true
                                checkable: true
                                checked: (root.settings?.flavor || "tonal-spot") === modelData
                                onClicked: if(root.settings) root.settings.flavor = modelData
                            }
                        }
                    }
                }

                // --- 分割线 ---
                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: Kirigami.Theme.textColor
                    opacity: 0.1
                    Layout.topMargin: Kirigami.Units.mediumSpacing
                    Layout.bottomMargin: Kirigami.Units.mediumSpacing
                }

                // --- 底部状态 ---
                RowLayout {
                    Layout.fillWidth: true
                    Layout.margins: Kirigami.Units.largeSpacing
                    spacing: Kirigami.Units.mediumSpacing
                    opacity: 0.6

                    Kirigami.Icon {
                        source: "dialog-information"
                        Layout.preferredWidth: Kirigami.Units.iconSizes.small
                        Layout.preferredHeight: Kirigami.Units.iconSizes.small
                    }

                    PlasmaComponents.Label {
                        text: "Themes will update automatically."
                        font: Kirigami.Theme.smallFont
                        Layout.fillWidth: true
                        wrapMode: Text.WordWrap
                    }
                }

                // 底部留白
                Item { height: Kirigami.Units.mediumSpacing }
            }
        }
    }
}
