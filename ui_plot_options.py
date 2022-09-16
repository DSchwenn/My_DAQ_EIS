/********************************************************************************
** Form generated from reading UI file 'plot_options.ui'
**
** Created by: Qt User Interface Compiler version 5.9.7
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_PLOT_OPTIONS_H
#define UI_PLOT_OPTIONS_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QCheckBox>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QDoubleSpinBox>
#include <QtWidgets/QGroupBox>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLabel>
#include <QtWidgets/QListWidget>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_Form
{
public:
    QComboBox *comboBox;
    QLabel *label;
    QGroupBox *groupBox;
    QDoubleSpinBox *doubleSpinBox;
    QDoubleSpinBox *doubleSpinBox_2;
    QLabel *label_4;
    QLabel *label_5;
    QCheckBox *checkBox_2;
    QGroupBox *groupBox_2;
    QComboBox *comboBox_2;
    QLabel *label_2;
    QLabel *label_3;
    QComboBox *comboBox_3;
    QCheckBox *checkBox;
    QLabel *label_6;
    QListWidget *listWidget;
    QComboBox *comboBox_4;

    void setupUi(QWidget *Form)
    {
        if (Form->objectName().isEmpty())
            Form->setObjectName(QStringLiteral("Form"));
        Form->resize(182, 426);
        comboBox = new QComboBox(Form);
        comboBox->setObjectName(QStringLiteral("comboBox"));
        comboBox->setGeometry(QRect(79, 10, 81, 22));
        label = new QLabel(Form);
        label->setObjectName(QStringLiteral("label"));
        label->setGeometry(QRect(6, 10, 61, 16));
        groupBox = new QGroupBox(Form);
        groupBox->setObjectName(QStringLiteral("groupBox"));
        groupBox->setGeometry(QRect(10, 70, 161, 111));
        doubleSpinBox = new QDoubleSpinBox(groupBox);
        doubleSpinBox->setObjectName(QStringLiteral("doubleSpinBox"));
        doubleSpinBox->setGeometry(QRect(70, 40, 81, 22));
        doubleSpinBox->setMinimum(0);
        doubleSpinBox->setMaximum(100000);
        doubleSpinBox->setValue(80);
        doubleSpinBox_2 = new QDoubleSpinBox(groupBox);
        doubleSpinBox_2->setObjectName(QStringLiteral("doubleSpinBox_2"));
        doubleSpinBox_2->setGeometry(QRect(71, 70, 81, 22));
        label_4 = new QLabel(groupBox);
        label_4->setObjectName(QStringLiteral("label_4"));
        label_4->setGeometry(QRect(10, 70, 47, 14));
        label_5 = new QLabel(groupBox);
        label_5->setObjectName(QStringLiteral("label_5"));
        label_5->setGeometry(QRect(10, 40, 61, 16));
        checkBox_2 = new QCheckBox(groupBox);
        checkBox_2->setObjectName(QStringLiteral("checkBox_2"));
        checkBox_2->setGeometry(QRect(10, 20, 131, 18));
        groupBox_2 = new QGroupBox(Form);
        groupBox_2->setObjectName(QStringLiteral("groupBox_2"));
        groupBox_2->setGeometry(QRect(10, 200, 161, 161));
        comboBox_2 = new QComboBox(groupBox_2);
        comboBox_2->setObjectName(QStringLiteral("comboBox_2"));
        comboBox_2->setGeometry(QRect(70, 20, 81, 22));
        label_2 = new QLabel(groupBox_2);
        label_2->setObjectName(QStringLiteral("label_2"));
        label_2->setGeometry(QRect(10, 20, 41, 16));
        label_3 = new QLabel(groupBox_2);
        label_3->setObjectName(QStringLiteral("label_3"));
        label_3->setGeometry(QRect(10, 110, 31, 16));
        comboBox_3 = new QComboBox(groupBox_2);
        comboBox_3->setObjectName(QStringLiteral("comboBox_3"));
        comboBox_3->setGeometry(QRect(50, 110, 101, 22));
        checkBox = new QCheckBox(groupBox_2);
        checkBox->setObjectName(QStringLiteral("checkBox"));
        checkBox->setGeometry(QRect(10, 140, 81, 18));
        label_6 = new QLabel(groupBox_2);
        label_6->setObjectName(QStringLiteral("label_6"));
        label_6->setGeometry(QRect(10, 50, 16, 16));
        listWidget = new QListWidget(groupBox_2);
        listWidget->setObjectName(QStringLiteral("listWidget"));
        listWidget->setGeometry(QRect(30, 50, 121, 51));
        comboBox_4 = new QComboBox(Form);
        comboBox_4->setObjectName(QStringLiteral("comboBox_4"));
        comboBox_4->setGeometry(QRect(80, 40, 81, 22));

        retranslateUi(Form);

        QMetaObject::connectSlotsByName(Form);
    } // setupUi

    void retranslateUi(QWidget *Form)
    {
        Form->setWindowTitle(QApplication::translate("Form", "Form", Q_NULLPTR));
        label->setText(QApplication::translate("Form", "Channel in:", Q_NULLPTR));
        groupBox->setTitle(QApplication::translate("Form", "Curve", Q_NULLPTR));
        label_4->setText(QApplication::translate("Form", "x-Time:", Q_NULLPTR));
        label_5->setText(QApplication::translate("Form", "Frequency:", Q_NULLPTR));
        checkBox_2->setText(QApplication::translate("Form", "Subsample", Q_NULLPTR));
        groupBox_2->setTitle(QApplication::translate("Form", "FFT plot", Q_NULLPTR));
        label_2->setText(QApplication::translate("Form", "F from:", Q_NULLPTR));
        label_3->setText(QApplication::translate("Form", "Type:", Q_NULLPTR));
        checkBox->setText(QApplication::translate("Form", "Plot phase", Q_NULLPTR));
        label_6->setText(QApplication::translate("Form", "F:", Q_NULLPTR));
    } // retranslateUi

};

namespace Ui {
    class Form: public Ui_Form {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_PLOT_OPTIONS_H
