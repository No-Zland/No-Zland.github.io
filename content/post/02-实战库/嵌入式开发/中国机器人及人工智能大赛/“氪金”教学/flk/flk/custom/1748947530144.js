Blockly.Blocks['1748947530144'] = {
  init: function() {
    this.jsonInit({
      "type": "1748947530144",
      "message0": "高台抱",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1748947530144'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(86,23,156,93,160,150,70,95,130,167,45,95,40,50,130,98,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,10,156,93,160,150,70,95,136,180,44,95,40,50,130,98,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,10,156,100,107,50,138,97,136,180,44,101,91,137,72,99,120,40,99)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1748947530144'] = function(block) {
  let code = "robot.leju_action('高台抱')\n";
  return code;
}

