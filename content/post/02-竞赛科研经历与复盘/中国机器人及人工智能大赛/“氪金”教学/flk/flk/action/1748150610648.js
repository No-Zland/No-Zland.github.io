Blockly.Blocks['1748150610648'] = {
  init: function() {
    this.jsonInit({
      "type": "1748150610648",
      "message0": "2块左转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1748150610648'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(25)\nMOTOmove19(66,26,189,95,49,50,87,96,129,175,10,97,88,181,20,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(66,26,189,100,93,55,124,100,129,175,10,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1748150610648'] = function(block) {
  let code = "robot.leju_action('2块左转')\n";
  return code;
}

