Blockly.Blocks['1710422585740'] = {
  init: function() {
    this.jsonInit({
      "type": "1710422585740",
      "message0": "后退2(1)",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1710422585740'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 99, 58, 51, 106, 100, 120, 170, 100, 102, 109, 134, 75, 100, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 105, 91, 56, 132, 96, 120, 170, 100, 107, 126, 114, 108, 99, 128, 71, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 128, 71, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1710422585740'] = function(block) {
  let code = "robot.leju_action('后退2(1)')\n";
  return code;
}

