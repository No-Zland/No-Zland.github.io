Blockly.Blocks['1747818499673'] = {
  init: function() {
    this.jsonInit({
      "type": "1747818499673",
      "message0": "bao1kuaiquanzou",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": '#C643F1',
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1747818499673'] = function(block) {
  let code = "MOTOsetspeed(30)\nMOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65,0,0,0)\nMOTOsetspeed(50)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(64, 10, 180, 90, 98, 47, 133, 86, 137, 190, 23, 94, 107, 146, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64, 10, 180, 86, 113, 37, 156, 88, 137, 190, 23, 94, 107, 146, 77, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(64, 10, 180, 107, 100, 56, 124, 111, 137, 190, 23, 112, 129, 155, 93, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 95, 54, 123, 113, 137, 190, 23, 114, 75, 105, 90, 110, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 106, 93, 54, 123, 111, 137, 190, 23, 114, 87, 163, 44, 112, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(64, 10, 180, 88, 71, 45, 107, 90, 137, 190, 23, 93, 100, 144, 76, 89, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(45)\nMOTOmove19(64, 10, 180, 86, 125, 95, 110, 90, 137, 190, 23, 94, 107, 146, 76, 87, 120, 40, 100)\nMOTOwait()\nMOTOsetspeed(8)\nMOTOmove19(64, 10, 180, 100, 93, 55, 124, 100, 137, 190, 23, 100, 107, 145, 76, 100, 120, 40, 100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1747818499673'] = function(block) {
  let code = "robot.leju_action('bao1kuaiquanzou')\n";
  return code;
}

