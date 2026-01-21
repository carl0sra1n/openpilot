/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other
 * contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/torque_lateral_control_custom_params.h"

TorqueLateralControlCustomParams::TorqueLateralControlCustomParams(
    const QString &param, const QString &title, const QString &description,
    const QString &icon, QWidget *parent)
    : ExpandableToggleRow(param, title, description, icon, parent) {

  QFrame *frame = new QFrame(this);
  QGridLayout *frame_layout = new QGridLayout();
  frame->setLayout(frame_layout);
  frame_layout->setSpacing(0);

  torqueLateralControlParamsOverride = new ParamControl(
      "TorqueParamsOverrideEnabled", tr("Manual Real-Time Tuning"),
      tr("Enforces the torque lateral controller to use the fixed values "
         "instead of the learned values from Self-Tune. Enabling this toggle "
         "overrides Self-Tune values."),
      "../assets/offroad/icon_blank.png", this);
  connect(torqueLateralControlParamsOverride, &ParamControl::toggleFlipped,
          this, &TorqueLateralControlCustomParams::refresh);

  torqueParamsOverrideLatAccelFactor = new OptionControlSP(
      "TorqueParamsOverrideLatAccelFactor", tr("Lateral Acceleration Factor"),
      "", "", {1, 500}, 1, false, nullptr, true, false);
  connect(torqueParamsOverrideLatAccelFactor, &OptionControlSP::updateLabels,
          this, &TorqueLateralControlCustomParams::refresh);
  torqueParamsOverrideLatAccelFactor->setFixedWidth(280);

  torqueParamsOverrideFriction =
      new OptionControlSP("TorqueParamsOverrideFriction", tr("Friction"), "",
                          "", {1, 100}, 1, false, nullptr, true, false);
  connect(torqueParamsOverrideFriction, &OptionControlSP::updateLabels, this,
          &TorqueLateralControlCustomParams::refresh);
  torqueParamsOverrideFriction->setFixedWidth(280);

  liveTuningKp =
      new OptionControlSP("LiveTuningKp", tr("Proportional (kP)"), "", "",
                          {0, 50}, 1, false, nullptr, true, false);
  connect(liveTuningKp, &OptionControlSP::updateLabels, this,
          &TorqueLateralControlCustomParams::refresh);
  liveTuningKp->setFixedWidth(280);

  liveTuningKi =
      new OptionControlSP("LiveTuningKi", tr("Integral (kI)"), "", "", {0, 30},
                          1, false, nullptr, true, false);
  connect(liveTuningKi, &OptionControlSP::updateLabels, this,
          &TorqueLateralControlCustomParams::refresh);
  liveTuningKi->setFixedWidth(280);

  liveTuningKf =
      new OptionControlSP("LiveTuningKf", tr("Feed-Forward (kF)"), "", "",
                          {0, 100}, 1, false, nullptr, true, false);
  connect(liveTuningKf, &OptionControlSP::updateLabels, this,
          &TorqueLateralControlCustomParams::refresh);
  liveTuningKf->setFixedWidth(280);

  liveTuningDeadzone =
      new OptionControlSP("LiveTuningDeadzone", tr("Deadzone (deg)"), "", "",
                          {0, 20}, 1, false, nullptr, true, false);
  connect(liveTuningDeadzone, &OptionControlSP::updateLabels, this,
          &TorqueLateralControlCustomParams::refresh);
  liveTuningDeadzone->setFixedWidth(280);

  frame_layout->addWidget(torqueLateralControlParamsOverride, 0, 0, 1, 2);
  QSpacerItem *spacer = new QSpacerItem(20, 40);
  frame_layout->addItem(spacer, 1, 0, 1, 2);
  frame_layout->addWidget(torqueParamsOverrideLatAccelFactor, 2, 0,
                          Qt::AlignCenter);
  frame_layout->addWidget(torqueParamsOverrideFriction, 2, 1, Qt::AlignCenter);
  frame_layout->addWidget(liveTuningKp, 3, 0, Qt::AlignCenter);
  frame_layout->addWidget(liveTuningKi, 3, 1, Qt::AlignCenter);
  frame_layout->addWidget(liveTuningKf, 4, 0, Qt::AlignCenter);
  frame_layout->addWidget(liveTuningDeadzone, 4, 1, Qt::AlignCenter);

  addItem(frame);

  refresh();
}

void TorqueLateralControlCustomParams::refresh() {
  bool torque_override_param = params.getBool("TorqueParamsOverrideEnabled");
  float laf_param =
      QString::fromStdString(params.get("TorqueParamsOverrideLatAccelFactor"))
          .toFloat();
  const QString laf_unit = "m/s²";

  float friction_param =
      QString::fromStdString(params.get("TorqueParamsOverrideFriction"))
          .toFloat();
  float kp_param = QString::fromStdString(params.get("LiveTuningKp")).toFloat();
  float ki_param = QString::fromStdString(params.get("LiveTuningKi")).toFloat();
  float kf_param = QString::fromStdString(params.get("LiveTuningKf")).toFloat();
  float deadzone_param =
      QString::fromStdString(params.get("LiveTuningDeadzone")).toFloat();

  torqueParamsOverrideLatAccelFactor->setTitle(
      tr("Lateral Acceleration Factor") + "\n(" +
      (torque_override_param ? tr("Real-time and Offline")
                             : tr("Offline Only")) +
      ")");
  torqueParamsOverrideFriction->setTitle(tr("Friction") + "\n(" +
                                         (torque_override_param
                                              ? tr("Real-time and Offline")
                                              : tr("Offline Only")) +
                                         ")");

  torqueParamsOverrideLatAccelFactor->setLabel(
      QString::number(laf_param, 'f', 2) + " " + laf_unit);
  torqueParamsOverrideFriction->setLabel(
      QString::number(friction_param, 'f', 2));
  liveTuningKp->setLabel(QString::number(kp_param, 'f', 2));
  liveTuningKi->setLabel(QString::number(ki_param, 'f', 2));
  liveTuningKf->setLabel(QString::number(kf_param, 'f', 5));
  liveTuningDeadzone->setLabel(QString::number(deadzone_param, 'f', 1) +
                               " deg");
}
