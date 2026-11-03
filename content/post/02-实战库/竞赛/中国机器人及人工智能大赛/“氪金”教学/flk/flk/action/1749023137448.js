Blockly.Blocks['1749023137448'] = {
  init: function() {
    this.jsonInit({
      "type": "1749023137448",
      "message0": "高台左转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1749023137448'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(25)\nMOTOmove19(80,10,156,95,49,50,87,96,136,180,44,97,88,181,20,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(80,10,156,100,93,55,124,100,136,180,44,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1749023137448'] = function(block) {
  let code = "robot.leju_action('高台左转')\n";
  return code;
}

