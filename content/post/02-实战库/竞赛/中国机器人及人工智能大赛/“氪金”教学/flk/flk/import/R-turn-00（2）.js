Blockly.Blocks['1711261612064'] = {
  init: function() {
    this.jsonInit({
      "type": "1711261612064",
      "message0": "R-turn-00（2）",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711261612064'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(68, 32, 90, 91, 132, 34, 190, 91, 129, 162, 105, 106, 167, 138, 137, 104, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80, 30, 100, 100, 93, 55, 124, 100, 120, 170, 100, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711261612064'] = function(block) {
  let code = "robot.leju_action('R-turn-00（2）')\n";
  return code;
}

