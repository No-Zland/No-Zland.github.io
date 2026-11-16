Blockly.Blocks['1752896312188'] = {
  init: function() {
    this.jsonInit({
      "type": "1752896312188",
      "message0": "z1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752896312188'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(58,24,180,100,93,55,124,100,123,188,22,99,107,144,75,99,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,180,100,93,55,124,100,123,188,22,109,106,144,78,104,120,40,99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(58,24,180,100,93,55,124,100,123,188,22,99,107,144,75,99,120,40,99)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752896312188'] = function(block) {
  let code = "robot.leju_action('z1')\n";
  return code;
}

