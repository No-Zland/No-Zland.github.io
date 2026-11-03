Blockly.Blocks['1752580328300'] = {
  init: function() {
    this.jsonInit({
      "type": "1752580328300",
      "message0": "叠块小右转1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752580328300'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(15)\nMOTOmove19(66,26,190,97,99,42,143,95,130,176,10,99,131,154,89,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(66,26,190,100,93,55,124,100,130,176,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752580328300'] = function(block) {
  let code = "robot.leju_action('叠块小右转1')\n";
  return code;
}

