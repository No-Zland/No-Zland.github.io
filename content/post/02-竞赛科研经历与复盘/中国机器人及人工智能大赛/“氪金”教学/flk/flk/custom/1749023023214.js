Blockly.Blocks['1749023023214'] = {
  init: function() {
    this.jsonInit({
      "type": "1749023023214",
      "message0": "高台右转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1749023023214'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(30)\nMOTOmove19(80,10,156,87,114,34,172,90,136,180,44,108,149,157,104,108,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,10,156,100,93,55,124,100,136,180,44,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1749023023214'] = function(block) {
  let code = "robot.leju_action('高台右转')\n";
  return code;
}

