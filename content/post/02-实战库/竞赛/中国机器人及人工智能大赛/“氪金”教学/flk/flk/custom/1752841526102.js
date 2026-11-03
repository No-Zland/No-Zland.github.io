Blockly.Blocks['1752841526102'] = {
  init: function() {
    this.jsonInit({
      "type": "1752841526102",
      "message0": "diekuaizuozuan1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752841526102'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(20)\nMOTOmove19(58,24,189,95,91,64,112,95,123,188,10,96,101,182,35,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(58,24,189,100,93,55,124,100,123,188,10,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752841526102'] = function(block) {
  let code = "robot.leju_action('diekuaizuozuan1')\n";
  return code;
}

