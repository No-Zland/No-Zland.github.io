Blockly.Blocks['1711262014402'] = {
  init: function() {
    this.jsonInit({
      "type": "1711262014402",
      "message0": "Box-Rturn1",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711262014402'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 85, 102, 160, 60, 177, 95, 120, 170, 85, 101, 150, 133, 144, 93, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nDelayMs(800)\n";
  return code;
}

Blockly.Python['1711262014402'] = function(block) {
  let code = "robot.leju_action('Box-Rturn1')\n";
  return code;
}

