Blockly.Blocks['1711174602361'] = {
  init: function() {
    this.jsonInit({
      "type": "1711174602361",
      "message0": "L-turn-00",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711174602361'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,20,20,75,65,65,65,65,30,20,20,65,75,65,65,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 115, 94, 29, 56, 57, 92, 120, 170, 115, 103, 48, 146, 14, 104, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nDelayMs(800)\n";
  return code;
}

Blockly.Python['1711174602361'] = function(block) {
  let code = "robot.leju_action('L-turn-00')\n";
  return code;
}

