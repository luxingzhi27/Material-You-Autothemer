import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.kirigami as Kirigami
import Qt.labs.platform 1.1
import Qt.labs.settings 1.0

PlasmoidItem {
    id: root

    // 处理路径：去掉 file:// 前缀
    readonly property string configPath: StandardPaths.writableLocation(StandardPaths.ConfigLocation).toString().replace("file://", "") + "/matugen-kde/config.conf"

    Settings {
        id: appSettings
        category: "General"
        fileName: root.configPath

        property string colorMode: "dark"
        property string flavor: "tonal-spot"
    }

    compactRepresentation: CompactRepresentation {}

    fullRepresentation: FullRepresentation {
        settings: appSettings
    }

    preferredRepresentation: compactRepresentation
}
