/********************************************************************************
** Form generated from reading UI file 'tst.ui'
**
** Created by: Qt User Interface Compiler version 5.9.7
**
** WARNING! All changes made in this file will be lost when recompiling UI file!
********************************************************************************/

#ifndef UI_TST_H
#define UI_TST_H

#include <QtCore/QVariant>
#include <QtWidgets/QAction>
#include <QtWidgets/QApplication>
#include <QtWidgets/QButtonGroup>
#include <QtWidgets/QComboBox>
#include <QtWidgets/QDoubleSpinBox>
#include <QtWidgets/QFrame>
#include <QtWidgets/QHBoxLayout>
#include <QtWidgets/QHeaderView>
#include <QtWidgets/QLabel>
#include <QtWidgets/QListWidget>
#include <QtWidgets/QMainWindow>
#include <QtWidgets/QMenu>
#include <QtWidgets/QMenuBar>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QStatusBar>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QWidget>

QT_BEGIN_NAMESPACE

class Ui_MainWindow
{
public:
    QAction *actionAction_1;
    QAction *actionSub_1;
    QAction *actionSub_2;
    QAction *actionNothing;
    QWidget *centralwidget;
    QVBoxLayout *verticalLayout_2;
    QVBoxLayout *verticalLayout;
    QWidget *test_widget;
    QHBoxLayout *horizontalLayout;
    QPushButton *pushButton_1;
    QPushButton *pushButton_3;
    QPushButton *pushButton_2;
    QFrame *line_4;
    QHBoxLayout *horizontalLayout_2;
    QListWidget *listWidget;
    QFrame *line;
    QComboBox *comboBox;
    QFrame *line_2;
    QDoubleSpinBox *doubleSpinBox;
    QFrame *line_3;
    QLabel *label;
    QMenuBar *menubar;
    QMenu *menuFile;
    QMenu *menuAction_2;
    QMenu *menuMenu_2;
    QStatusBar *statusbar;

    void setupUi(QMainWindow *MainWindow)
    {
        if (MainWindow->objectName().isEmpty())
            MainWindow->setObjectName(QStringLiteral("MainWindow"));
        MainWindow->resize(383, 337);
        actionAction_1 = new QAction(MainWindow);
        actionAction_1->setObjectName(QStringLiteral("actionAction_1"));
        actionSub_1 = new QAction(MainWindow);
        actionSub_1->setObjectName(QStringLiteral("actionSub_1"));
        actionSub_2 = new QAction(MainWindow);
        actionSub_2->setObjectName(QStringLiteral("actionSub_2"));
        actionNothing = new QAction(MainWindow);
        actionNothing->setObjectName(QStringLiteral("actionNothing"));
        centralwidget = new QWidget(MainWindow);
        centralwidget->setObjectName(QStringLiteral("centralwidget"));
        verticalLayout_2 = new QVBoxLayout(centralwidget);
        verticalLayout_2->setObjectName(QStringLiteral("verticalLayout_2"));
        verticalLayout = new QVBoxLayout();
        verticalLayout->setObjectName(QStringLiteral("verticalLayout"));
        test_widget = new QWidget(centralwidget);
        test_widget->setObjectName(QStringLiteral("test_widget"));

        verticalLayout->addWidget(test_widget);

        horizontalLayout = new QHBoxLayout();
        horizontalLayout->setObjectName(QStringLiteral("horizontalLayout"));
        pushButton_1 = new QPushButton(centralwidget);
        pushButton_1->setObjectName(QStringLiteral("pushButton_1"));

        horizontalLayout->addWidget(pushButton_1);

        pushButton_3 = new QPushButton(centralwidget);
        pushButton_3->setObjectName(QStringLiteral("pushButton_3"));

        horizontalLayout->addWidget(pushButton_3);

        pushButton_2 = new QPushButton(centralwidget);
        pushButton_2->setObjectName(QStringLiteral("pushButton_2"));

        horizontalLayout->addWidget(pushButton_2);


        verticalLayout->addLayout(horizontalLayout);

        line_4 = new QFrame(centralwidget);
        line_4->setObjectName(QStringLiteral("line_4"));
        line_4->setFrameShape(QFrame::HLine);
        line_4->setFrameShadow(QFrame::Sunken);

        verticalLayout->addWidget(line_4);

        horizontalLayout_2 = new QHBoxLayout();
        horizontalLayout_2->setObjectName(QStringLiteral("horizontalLayout_2"));
        listWidget = new QListWidget(centralwidget);
        listWidget->setObjectName(QStringLiteral("listWidget"));

        horizontalLayout_2->addWidget(listWidget);

        line = new QFrame(centralwidget);
        line->setObjectName(QStringLiteral("line"));
        line->setFrameShape(QFrame::VLine);
        line->setFrameShadow(QFrame::Sunken);

        horizontalLayout_2->addWidget(line);

        comboBox = new QComboBox(centralwidget);
        comboBox->setObjectName(QStringLiteral("comboBox"));

        horizontalLayout_2->addWidget(comboBox);

        line_2 = new QFrame(centralwidget);
        line_2->setObjectName(QStringLiteral("line_2"));
        line_2->setFrameShape(QFrame::VLine);
        line_2->setFrameShadow(QFrame::Sunken);

        horizontalLayout_2->addWidget(line_2);

        doubleSpinBox = new QDoubleSpinBox(centralwidget);
        doubleSpinBox->setObjectName(QStringLiteral("doubleSpinBox"));

        horizontalLayout_2->addWidget(doubleSpinBox);


        verticalLayout->addLayout(horizontalLayout_2);

        line_3 = new QFrame(centralwidget);
        line_3->setObjectName(QStringLiteral("line_3"));
        line_3->setFrameShape(QFrame::HLine);
        line_3->setFrameShadow(QFrame::Sunken);

        verticalLayout->addWidget(line_3);

        label = new QLabel(centralwidget);
        label->setObjectName(QStringLiteral("label"));

        verticalLayout->addWidget(label);

        verticalLayout->setStretch(0, 4);
        verticalLayout->setStretch(1, 1);
        verticalLayout->setStretch(3, 1);

        verticalLayout_2->addLayout(verticalLayout);

        MainWindow->setCentralWidget(centralwidget);
        menubar = new QMenuBar(MainWindow);
        menubar->setObjectName(QStringLiteral("menubar"));
        menubar->setGeometry(QRect(0, 0, 383, 22));
        menuFile = new QMenu(menubar);
        menuFile->setObjectName(QStringLiteral("menuFile"));
        menuAction_2 = new QMenu(menuFile);
        menuAction_2->setObjectName(QStringLiteral("menuAction_2"));
        menuMenu_2 = new QMenu(menubar);
        menuMenu_2->setObjectName(QStringLiteral("menuMenu_2"));
        MainWindow->setMenuBar(menubar);
        statusbar = new QStatusBar(MainWindow);
        statusbar->setObjectName(QStringLiteral("statusbar"));
        MainWindow->setStatusBar(statusbar);

        menubar->addAction(menuFile->menuAction());
        menubar->addAction(menuMenu_2->menuAction());
        menuFile->addAction(actionAction_1);
        menuFile->addSeparator();
        menuFile->addAction(menuAction_2->menuAction());
        menuAction_2->addAction(actionSub_1);
        menuAction_2->addAction(actionSub_2);
        menuMenu_2->addAction(actionNothing);

        retranslateUi(MainWindow);

        QMetaObject::connectSlotsByName(MainWindow);
    } // setupUi

    void retranslateUi(QMainWindow *MainWindow)
    {
        MainWindow->setWindowTitle(QApplication::translate("MainWindow", "MainWindow", Q_NULLPTR));
        actionAction_1->setText(QApplication::translate("MainWindow", "Action 1", Q_NULLPTR));
        actionSub_1->setText(QApplication::translate("MainWindow", "Sub 1", Q_NULLPTR));
        actionSub_2->setText(QApplication::translate("MainWindow", "Sub 2", Q_NULLPTR));
        actionNothing->setText(QApplication::translate("MainWindow", "Nothing", Q_NULLPTR));
        pushButton_1->setText(QApplication::translate("MainWindow", "Do", Q_NULLPTR));
        pushButton_3->setText(QApplication::translate("MainWindow", "Re", Q_NULLPTR));
        pushButton_2->setText(QApplication::translate("MainWindow", "Mi", Q_NULLPTR));
        label->setText(QApplication::translate("MainWindow", "TextLabel", Q_NULLPTR));
        menuFile->setTitle(QApplication::translate("MainWindow", "File", Q_NULLPTR));
        menuAction_2->setTitle(QApplication::translate("MainWindow", "Action 2", Q_NULLPTR));
        menuMenu_2->setTitle(QApplication::translate("MainWindow", "Menu 2", Q_NULLPTR));
    } // retranslateUi

};

namespace Ui {
    class MainWindow: public Ui_MainWindow {};
} // namespace Ui

QT_END_NAMESPACE

#endif // UI_TST_H
