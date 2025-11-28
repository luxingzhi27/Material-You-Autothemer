import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Controls.Material
import Qt.labs.platform

ApplicationWindow {
    id: window
    visible: true
    width: 900
    height: 600
    minimumWidth: 900
    minimumHeight: 600
    title: "Material You Color"
    flags: Qt.Window | Qt.FramelessWindowHint
    color: "transparent"

    // Backend properties
    property string currentMode: pythonBackend ? pythonBackend.colorMode : "dark"
    property string currentFlavor: pythonBackend ? pythonBackend.flavor : "tonal-spot"
    property var themeColors: (pythonBackend && pythonBackend.previewTheme && Object.keys(pythonBackend.previewTheme).length > 0) ? pythonBackend.previewTheme : null

    // Helper to safely get color
    function getColor(key, fallback) {
        if (themeColors && themeColors[key]) return themeColors[key];
        return fallback;
    }

    function getFlavorDescription(flavor) {
        switch(flavor) {
            case "tonal-spot": return "Default. Balanced colors with medium contrast.";
            case "vibrant": return "More colorful. Higher saturation and contrast.";
            case "expressive": return "Playful. Shifts hues for a unique look.";
            case "fruit-salad": return "Very colorful. High saturation and variety.";
            case "content": return "Natural. Uses colors directly from the image.";
            case "neutral": return "Subtle. Low saturation, near grayscale.";
            case "rainbow": return "Dynamic. A wide range of colors.";
            case "fidelity": return "Accurate. Matches the image colors closely.";
            default: return "";
        }
    }

    property string tooltipText: ""
    property point tooltipPos: Qt.point(0, 0)

    Rectangle {
        id: floatingTooltip
        z: 999
        visible: tooltipText !== ""
        color: getColor("inverse_surface", "#313033")
        radius: 4
        width: tooltipLabel.width + 16
        height: tooltipLabel.height + 10
        x: tooltipPos.x + 12
        y: tooltipPos.y + 12

        Label {
            id: tooltipLabel
            anchors.centerIn: parent
            text: tooltipText
            color: getColor("inverse_on_surface", "#F4EFF4")
            font.pixelSize: 12
        }
    }

    // Material Theme Setup
    Material.theme: currentMode === "dark" ? Material.Dark : Material.Light
    Material.primary: getColor("primary", "#6750A4")
    Material.accent: getColor("tertiary", "#7D5260")

    // Main Background with Rounded Corners
    Rectangle {
        id: mainBackground
        anchors.fill: parent
        anchors.margins: window.visibility === Window.Maximized ? 0 : 0
        radius: window.visibility === Window.Maximized ? 0 : 16
        color: getColor("background", currentMode === "dark" ? "#1c1b1f" : "#fffbfe")
        border.color: getColor("outline", "#79747E")
        border.width: window.visibility === Window.Maximized ? 0 : 1
        clip: true

        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            // --- Custom Title Bar ---
            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                color: getColor("surface", "#1c1b1f")
                z: 10

                RowLayout {
                    anchors.fill: parent
                    spacing: 0

                    // Drag Area
                    Item {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        MouseArea {
                            anchors.fill: parent
                            onPressed: window.startSystemMove()
                            onDoubleClicked: window.visibility === Window.Maximized ? window.showNormal() : window.showMaximized()
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.leftMargin: 16

                            Label {
                                text: window.title
                                font.weight: Font.Bold
                                font.pixelSize: 14
                                color: getColor("on_surface", "#000000")
                            }
                        }
                    }

                    // Window Controls
                    RowLayout {
                        Layout.fillHeight: true
                        Layout.rightMargin: 8
                        spacing: 8

                        // Minimize
                        Button {
                            Layout.preferredWidth: 32
                            Layout.preferredHeight: 32
                            flat: true

                            background: Rectangle {
                                radius: 16
                                color: parent.hovered ? Qt.alpha(getColor("on_surface", "#000000"), 0.1) : "transparent"
                            }
                            contentItem: Text {
                                text: "─"
                                color: getColor("on_surface", "#000000")
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                            }
                            onClicked: window.showMinimized()
                        }

                        // Maximize/Restore
                        Button {
                            Layout.preferredWidth: 32
                            Layout.preferredHeight: 32
                            flat: true

                            background: Rectangle {
                                radius: 16
                                color: parent.hovered ? Qt.alpha(getColor("on_surface", "#000000"), 0.1) : "transparent"
                            }
                            contentItem: Text {
                                text: window.visibility === Window.Maximized ? "❐" : "□"
                                color: getColor("on_surface", "#000000")
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                            }
                            onClicked: window.visibility === Window.Maximized ? window.showNormal() : window.showMaximized()
                        }

                        // Close
                        Button {
                            Layout.preferredWidth: 32
                            Layout.preferredHeight: 32
                            flat: true

                            background: Rectangle {
                                radius: 16
                                color: parent.hovered ? getColor("primary", "#6750A4") : "transparent"
                            }
                            contentItem: Text {
                                text: "✕"
                                color: parent.hovered ? getColor("on_primary", "#FFFFFF") : getColor("on_surface", "#000000")
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                            }
                            onClicked: window.close()
                        }
                    }
                }
            }

            // --- Main Content ---
            RowLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 0

                // --- Left Panel: Wallpaper Selection ---
                Rectangle {
                    Layout.fillHeight: true
                    Layout.preferredWidth: 350
                    color: Qt.alpha(getColor("on_surface", "#000000"), 0.05)

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 16

                        Label {
                            text: "Wallpaper"
                            font.pixelSize: 24
                            font.weight: Font.Bold
                            color: getColor("on_surface", "#000000")
                        }

                        // Folder Selection
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Label {
                                text: "Select Wallpaper Folder"
                                font.pixelSize: 12
                                color: getColor("on_surface_variant", "#000000")
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 8

                                TextField {
                                    id: folderPath
                                    Layout.fillWidth: true
                                    text: pythonBackend ? pythonBackend.wallpaperFolder : ""
                                    readOnly: true
                                    placeholderText: ""
                                    selectByMouse: true
                                    color: getColor("on_surface", "#000000")
                                    background: Rectangle {
                                        color: "transparent"
                                        border.color: getColor("outline", "#79747E")
                                        border.width: 1
                                        radius: 4
                                    }
                                }
                                Button {
                                    text: "Browse"
                                    highlighted: true
                                    Material.background: Material.primary
                                    contentItem: Text {
                                        text: parent.text
                                        font: parent.font
                                        color: getColor("on_primary", "white")
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    onClicked: folderDialog.open()
                                }
                            }
                        }

                        // Wallpaper Grid
                        GridView {
                            id: wallGrid
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            cellWidth: width / 2
                            cellHeight: cellWidth * 0.75

                            model: pythonBackend ? pythonBackend.wallpaperList : []
                            delegate: Item {
                                width: wallGrid.cellWidth
                                height: wallGrid.cellHeight

                                Rectangle {
                                    anchors.fill: parent
                                    anchors.margins: 4
                                    color: "transparent"
                                    border.color: (pythonBackend && pythonBackend.currentWallpaper === modelData) ? Material.primary : "transparent"
                                    border.width: 3
                                    radius: 8

                                    Image {
                                        anchors.fill: parent
                                        anchors.margins: 3
                                        source: "file://" + modelData
                                        fillMode: Image.PreserveAspectCrop
                                        sourceSize.width: 200
                                        sourceSize.height: 200
                                        layer.enabled: true

                                        MouseArea {
                                            anchors.fill: parent
                                            onClicked: if(pythonBackend) pythonBackend.currentWallpaper = modelData
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                // --- Right Panel: Configuration & Preview ---
                ColumnLayout {
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    Layout.margins: 24
                    spacing: 20

                    Label {
                        text: "Theme Configuration"
                        font.pixelSize: 24
                        font.weight: Font.Bold
                        color: getColor("on_surface", "#000000")
                    }

                    // --- Palette Preview ---
                    Pane {
                        Layout.fillWidth: true
                        padding: 16
                        Material.elevation: 0
                        background: Rectangle {
                            color: Qt.alpha(getColor("on_surface", "#000000"), 0.05)
                            radius: 12
                        }

                        ColumnLayout {
                            width: parent.width
                            spacing: 12

                            Label {
                                text: "Generated Palette"
                                font.weight: Font.DemiBold
                                opacity: 0.8
                                color: getColor("on_surface", "#000000")
                            }

                            Flow {
                                Layout.fillWidth: true
                                spacing: 10

                                Repeater {
                                    model: pythonBackend ? pythonBackend.previewColors : []
                                    delegate: ColumnLayout {
                                        spacing: 4
                                        Rectangle {
                                            width: 50
                                            height: 50
                                            radius: 25
                                            color: modelData.color || "transparent"
                                            border.color: Qt.alpha(getColor("outline", "#000000"), 0.2)
                                            border.width: 1
                                            scale: paletteMa.containsMouse ? 1.1 : 1.0

                                            Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }
                                            Behavior on color { ColorAnimation { duration: 300 } }

                                            MouseArea {
                                                id: paletteMa
                                                anchors.fill: parent
                                                hoverEnabled: true
                                                onEntered: window.tooltipText = modelData.name + ": " + modelData.color
                                                onExited: window.tooltipText = ""
                                                onPositionChanged: (mouse) => {
                                                    var pos = mapToItem(window.contentItem, mouse.x, mouse.y)
                                                    window.tooltipPos = pos
                                                }
                                            }
                                        }
                                        TextField {
                                            text: modelData.color
                                            font.pixelSize: 10
                                            font.family: "Monospace"
                                            Layout.alignment: Qt.AlignHCenter
                                            readOnly: true
                                            selectByMouse: true
                                            background: Item {}
                                            padding: 0
                                            horizontalAlignment: Text.AlignHCenter
                                            color: getColor("on_surface", "#000000")
                                            opacity: 0.7
                                        }
                                        Label {
                                            text: modelData.name
                                            font.pixelSize: 9
                                            Layout.alignment: Qt.AlignHCenter
                                            opacity: 0.5
                                            elide: Text.ElideRight
                                            Layout.maximumWidth: 60
                                            color: getColor("on_surface", "#000000")
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // --- Settings Controls ---
                    GridLayout {
                        columns: 2
                        columnSpacing: 20
                        rowSpacing: 20

                        // Mode Selection (Segmented Button)
                        ColumnLayout {
                            Label {
                                text: "Color Mode"
                                font.weight: Font.Medium
                                color: getColor("on_surface", "#000000")
                            }

                            Rectangle {
                                Layout.preferredWidth: 200
                                Layout.preferredHeight: 40
                                radius: 20
                                border.color: getColor("outline", "#79747E")
                                border.width: 1
                                color: "transparent"

                                // Middle Divider
                                Rectangle {
                                    anchors.centerIn: parent
                                    width: 1
                                    height: parent.height
                                    color: getColor("outline", "#79747E")
                                }

                                RowLayout {
                                    anchors.fill: parent
                                    spacing: 0

                                    // Light Button
                                    Item {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        clip: true

                                        Rectangle {
                                            width: parent.width + 20
                                            height: parent.height
                                            anchors.left: parent.left
                                            radius: 20
                                            color: {
                                                if (currentMode === "light") return Material.primary
                                                if (lightMa.containsMouse) return Qt.alpha(getColor("on_surface", "#000000"), 0.1)
                                                return "transparent"
                                            }
                                        }

                                        Text {
                                            anchors.centerIn: parent
                                            text: "Light"
                                            font.weight: Font.Medium
                                            color: currentMode === "light" ? getColor("on_primary", "white") : getColor("on_surface", "#000000")
                                        }
                                        MouseArea {
                                            id: lightMa
                                            anchors.fill: parent
                                            onClicked: if(pythonBackend) pythonBackend.colorMode = "light"
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                        }
                                    }

                                    // Dark Button
                                    Item {
                                        Layout.fillWidth: true
                                        Layout.fillHeight: true
                                        clip: true

                                        Rectangle {
                                            width: parent.width + 20
                                            height: parent.height
                                            anchors.right: parent.right
                                            radius: 20
                                            color: {
                                                if (currentMode === "dark") return Material.primary
                                                if (darkMa.containsMouse) return Qt.alpha(getColor("on_surface", "#000000"), 0.1)
                                                return "transparent"
                                            }
                                        }

                                        Text {
                                            anchors.centerIn: parent
                                            text: "Dark"
                                            font.weight: Font.Medium
                                            color: currentMode === "dark" ? getColor("on_primary", "white") : getColor("on_surface", "#000000")
                                        }
                                        MouseArea {
                                            id: darkMa
                                            anchors.fill: parent
                                            onClicked: if(pythonBackend) pythonBackend.colorMode = "dark"
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                        }
                                    }
                                }
                            }
                        }

                        // Flavor Selection
                        ColumnLayout {
                            Layout.columnSpan: 2
                            Layout.fillWidth: true
                            Label {
                                text: "Flavor"
                                font.weight: Font.Medium
                                color: getColor("on_surface", "#000000")
                            }

                            Flow {
                                Layout.fillWidth: true
                                spacing: 8

                                Repeater {
                                    model: ["tonal-spot", "vibrant", "expressive", "fruit-salad", "content", "neutral", "rainbow", "fidelity"]
                                    delegate: Rectangle {
                                        width: flavorText.contentWidth + 32
                                        height: 32
                                        radius: 16
                                        scale: flavorMa.containsMouse ? 1.05 : 1.0
                                        Behavior on scale { NumberAnimation { duration: 200; easing.type: Easing.OutQuad } }

                                        color: {
                                            if (currentFlavor === modelData) return Material.primary
                                            if (flavorMa.containsMouse) return Qt.alpha(getColor("on_surface", "#000000"), 0.05)
                                            return "transparent"
                                        }
                                        border.color: currentFlavor === modelData ? "transparent" : getColor("outline", "#79747E")
                                        border.width: 1

                                        Text {
                                            id: flavorText
                                            anchors.centerIn: parent
                                            text: modelData.replace("-", " ")
                                            font.capitalization: Font.Capitalize
                                            font.weight: Font.Medium
                                            color: currentFlavor === modelData ? getColor("on_primary", "white") : getColor("on_surface", "#000000")
                                        }

                                        MouseArea {
                                            id: flavorMa
                                            anchors.fill: parent
                                            onClicked: if(pythonBackend) pythonBackend.flavor = modelData
                                            hoverEnabled: true
                                            cursorShape: Qt.PointingHandCursor
                                            onEntered: window.tooltipText = getFlavorDescription(modelData)
                                            onExited: window.tooltipText = ""
                                            onPositionChanged: (mouse) => {
                                                var pos = mapToItem(window.contentItem, mouse.x, mouse.y)
                                                window.tooltipPos = pos
                                            }
                                        }
                                    }
                                }
                            }


                        }
                    }

                    Item { Layout.fillHeight: true } // Spacer

                    // --- Apply Button ---
                    Button {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 56
                        text: "Apply Theme and Wallpaper"
                        font.weight: Font.Bold
                        font.pixelSize: 16

                        Material.background: Material.primary
                        Material.foreground: getColor("on_primary", "white")
                        Material.elevation: 2

                        onClicked: {
                            if(pythonBackend) pythonBackend.apply_theme()
                        }
                    }
                }
            }
        }
    }

    // Resize Areas
    MouseArea {
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: 10
        height: 10
        cursorShape: Qt.SizeFDiagCursor
        onPressed: window.startSystemResize(Qt.BottomEdge | Qt.RightEdge)
    }

    MouseArea {
        anchors.left: parent.left
        anchors.bottom: parent.bottom
        width: 10
        height: 10
        cursorShape: Qt.SizeBDiagCursor
        onPressed: window.startSystemResize(Qt.BottomEdge | Qt.LeftEdge)
    }

    MouseArea {
        anchors.right: parent.right
        anchors.top: parent.top
        width: 10
        height: 10
        cursorShape: Qt.SizeBDiagCursor
        onPressed: window.startSystemResize(Qt.TopEdge | Qt.RightEdge)
    }

    MouseArea {
        anchors.left: parent.left
        anchors.top: parent.top
        width: 10
        height: 10
        cursorShape: Qt.SizeFDiagCursor
        onPressed: window.startSystemResize(Qt.TopEdge | Qt.LeftEdge)
    }

    MouseArea {
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 10
        height: 5
        cursorShape: Qt.SizeVerCursor
        onPressed: window.startSystemResize(Qt.BottomEdge)
    }

    MouseArea {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 10
        height: 5
        cursorShape: Qt.SizeVerCursor
        onPressed: window.startSystemResize(Qt.TopEdge)
    }

    MouseArea {
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: 10
        width: 5
        cursorShape: Qt.SizeHorCursor
        onPressed: window.startSystemResize(Qt.LeftEdge)
    }

    MouseArea {
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.margins: 10
        width: 5
        cursorShape: Qt.SizeHorCursor
        onPressed: window.startSystemResize(Qt.RightEdge)
    }

    FolderDialog {
        id: folderDialog
        title: "Select Wallpaper Folder"
        currentFolder: pythonBackend ? "file://" + pythonBackend.wallpaperFolder : ""
        onAccepted: {
            if(pythonBackend) pythonBackend.wallpaperFolder = folder
        }
    }
}
