// gui_windows/MainWindow.h — Qt 6 port of unyts gui.py
//
// Layout mirrors the Python tkinter GUI 1:1:
//   Title | unit col | value col
//   from  | QLineEdit (+ completer) | QLineEdit
//   to    | QLineEdit (+ completer) | QLineEdit
//         |   [Convert button]      |
//         | □ repeat search         |
//         | status label (time)     |
//   ─ conversion path label (optional, scrolling marquee) ─
//
// Menu: File | Options (FVF, timeout, algorithm) | Help

#pragma once

#include <QMainWindow>
#include <QLineEdit>
#include <QPushButton>
#include <QCheckBox>
#include <QLabel>
#include <QCompleter>
#include <QTimer>
#include <QStringList>
#include <QString>
#include <optional>

class MainWindow : public QMainWindow {
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent = nullptr);
    ~MainWindow() override = default;

protected:
    // Forward Enter key from any input field to _calculate
    bool eventFilter(QObject* obj, QEvent* event) override;

private slots:
    void onConvert();          // Forward conversion (from → to)
    void onReverseConvert();   // Reverse conversion (to → from, triggered by Enter in to-value)

    // Menus
    void onSetFvf();
    void onSetTimeout();
    void onLoadMemory();
    void onSaveMemory();
    void onCleanMemory();
    void onAbout();
    void onDocumentation();

    // Marquee animation for long path strings
    void onMarqueeTick();

private:
    // ── Widget pointers ──────────────────────────────────────────────────────
    QLineEdit*   fromUnitEdit_  = nullptr;
    QLineEdit*   fromValueEdit_ = nullptr;
    QLineEdit*   toUnitEdit_    = nullptr;
    QLineEdit*   toValueEdit_   = nullptr;
    QPushButton* convertBtn_    = nullptr;
    QCheckBox*   repeatSearch_  = nullptr;
    QLabel*      statusLbl_     = nullptr;   // shows timing or error
    QLabel*      pathLbl_       = nullptr;   // conversion path marquee
    QWidget*     pathRow_       = nullptr;   // container (hidden when path off)

    QCompleter*  fromCompleter_ = nullptr;
    QCompleter*  toCompleter_   = nullptr;

    // ── State ────────────────────────────────────────────────────────────────
    QStringList  allUnits_;          // populated from C++ engine on startup
    double       fvf_       = 1.0;
    int          timeoutMs_ = 5000;
    bool         printPath_ = false;

    // Marquee
    QTimer       marqueeTimer_;
    QString      fullPathStr_;
    int          marqueePos_  = 0;
    bool         marqueeDir_  = true;   // true = scrolling right
    static constexpr int kMarqueeWidth = 60;  // visible chars
    static constexpr int kMarqueeSpeed = 120; // ms per tick
    static constexpr int kMarqueePause = 2000;// ms pause at ends

    // ── Helpers ──────────────────────────────────────────────────────────────
    void buildUi();
    void buildMenus();
    void populateUnits();

    std::optional<double> parseValue(const QString& s) const;
    void setStatus(const QString& msg, bool error = false);
    void displayPath(const QString& path);
    void startMarquee(const QString& path);
    void stopMarquee();

    void doConvert(bool reverse);
};
