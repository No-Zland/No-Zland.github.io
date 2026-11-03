Blockly.Blocks['1711096067753'] = {
  init: function() {
    this.jsonInit({
      "type": "1711096067753",
      "message0": "box-Rmove-q",
      "previousStatement": null,
      "nextStatement": null,
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1711096067753'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,0,0,0)\nMOTOsetspeed(30)\nMOTOmove19(58, 20, 173, 100, 113, 70, 123, 98, 144, 184, 35, 99, 87, 132, 76, 104, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(50)\nMOTOmove19(58, 20, 173, 53, 102, 40, 148, 81, 144, 184, 35, 115, 85, 130, 77, 136, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(58, 20, 173, 93, 113, 70, 123, 94, 144, 184, 35, 102, 87, 132, 76, 104, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(58, 20, 173, 100, 113, 70, 123, 98, 144, 184, 35, 99, 87, 132, 76, 104, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1711096067753'] = function(block) {
  let code = "robot.leju_action('box-Rmove-q')\n";
  return code;
}

