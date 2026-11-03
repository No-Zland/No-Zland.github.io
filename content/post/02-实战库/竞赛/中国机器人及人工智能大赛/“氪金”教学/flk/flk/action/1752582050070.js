Blockly.Blocks['1752582050070'] = {
  init: function() {
    this.jsonInit({
      "type": "1752582050070",
      "message0": "叠块右转1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752582050070'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(15)\nMOTOmove19(58,24,190,97,99,42,143,95,123,188,10,99,131,154,89,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(58,24,190,100,93,55,124,100,123,188,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752582050070'] = function(block) {
  let code = "robot.leju_action('叠块右转1')\n";
  return code;
}

