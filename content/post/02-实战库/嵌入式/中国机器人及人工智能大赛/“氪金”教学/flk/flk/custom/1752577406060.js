Blockly.Blocks['1752577406060'] = {
  init: function() {
    this.jsonInit({
      "type": "1752577406060",
      "message0": "叠块小右转",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752577406060'] = function(block) {
  let code = "MOTOrigid16(20,20,20,75,65,65,65,65,20,20,20,75,65,65,65,65)\nMOTOsetspeed(20)\nMOTOmove19(66,26,190,97,99,42,143,95,130,176,10,104,132,154,90,102,120,40,100)\nMOTOwait()\nDelayMs(5)\nMOTOsetspeed(20)\nMOTOmove19(66,26,190,100,93,55,124,100,130,176,10,100,107,145,76,100,120,40,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752577406060'] = function(block) {
  let code = "robot.leju_action('叠块小右转')\n";
  return code;
}

