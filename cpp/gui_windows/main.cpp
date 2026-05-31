// gui_windows/main.cpp — Entry point for the unyts Qt 6 Windows GUI

#include <QApplication>
#include <QIcon>
#include "MainWindow.h"

int main(int argc, char* argv[])
{
    QApplication app(argc, argv);
    app.setApplicationName("Unyts Converter");
    app.setApplicationVersion("0.1.0");
    app.setOrganizationName("unyts");
    app.setWindowIcon(QIcon(":/unyts_icon.ico"));

    MainWindow window;
    window.show();

    return app.exec();
}
