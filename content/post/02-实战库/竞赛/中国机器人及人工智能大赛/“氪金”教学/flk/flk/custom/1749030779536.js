Blockly.Blocks['1749030779536'] = {
  init: function() {
    this.jsonInit({
      "type": "1749030779536",
      "message0": "zhouyi",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1749030779536'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(64,11,162,75,109,78,117,69,138,188,37,144,85,117,82,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(70)\nMOTOmove19(64,11,162,93,113,70,123,94,138,188,37,102,87,132,76,104,128,71,100)\nMOTOwait()\nMOTOsetspeed(150)\nMOTOmove19(64,11,162,100,113,70,123,94,138,188,37,98,87,132,76,104,128,71,100)\nMOTOwait()\nDelayMs(10)\n";
  return code;
}

Blockly.Python['1749030779536'] = function(block) {
  let code = "robot.leju_action('zhouyi')\n";
  return code;
}

