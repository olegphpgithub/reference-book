
#include <QFile>
#include <qbytearray.h>
#include <QMessageBox>

#include "BigResource1.h"

BigResource1::BigResource1(QWidget *parent)
    : QMainWindow(parent)
{
    ui.setupUi(this);
	QFile f(":/BigResource1/res/_s9216_0.bin");
	if (f.open(QIODevice::ReadOnly))
	{
		QByteArray ba = f.read(16);
		f.close();
		QMessageBox msgBox;
		msgBox.setText(ba.toHex());
		msgBox.exec();
	}
}
