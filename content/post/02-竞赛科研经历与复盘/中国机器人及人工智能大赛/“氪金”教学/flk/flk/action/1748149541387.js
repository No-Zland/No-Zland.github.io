Blockly.Blocks['1748149541387'] = {
  init: function() {
    this.jsonInit({
      "type": "1748149541387",
      "message0": "抱块右转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1748149541387'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,100,137,190,37,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,91,107,33,167,91,137,190,37,105,152,154,106,103,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(64,10,164,100,93,55,124,100,137,190,37,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1748149541387'] = function(block) {
  let code = "robot.leju_action('抱块右转')\n";
  return code;
}

