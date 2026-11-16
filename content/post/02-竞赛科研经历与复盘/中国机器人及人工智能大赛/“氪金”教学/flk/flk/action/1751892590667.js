Blockly.Blocks['1751892590667'] = {
  init: function() {
    this.jsonInit({
      "type": "1751892590667",
      "message0": "box-up-max-1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1751892590667'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(74,43,93,94,116,150,41,94,121,168,115,96,76,50,154,97,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,75,137,94,116,150,41,94,121,144,67,96,76,50,154,97,120,40,99)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(74,75,137,95,125,148,39,94,121,144,67,96,73,50,162,96,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,20,142,95,125,148,39,94,121,186,57,96,73,50,162,96,120,40,99)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(74,20,142,94,105,150,42,94,121,186,57,96,95,50,161,95,120,40,99)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,20,142,100,93,55,124,100,121,186,57,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1751892590667'] = function(block) {
  let code = "robot.leju_action('box-up-max-1')\n";
  return code;
}

