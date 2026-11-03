Blockly.Blocks['1752842629148'] = {
  init: function() {
    this.jsonInit({
      "type": "1752842629148",
      "message0": "zz",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752842629148'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(20)\nMOTOmove19(58,24,189,95,91,64,112,95,123,188,10,96,101,182,35,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(58,24,189,100,93,55,124,100,123,188,10,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,189,100,93,55,124,100,123,188,10,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752842629148'] = function(block) {
  let code = "robot.leju_action('zz')\n";
  return code;
}

