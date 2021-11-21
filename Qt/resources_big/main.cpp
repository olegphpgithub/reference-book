#include "BigResource1.h"
#include <QtWidgets/QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    BigResource1 w;
    w.show();
    return a.exec();
}
