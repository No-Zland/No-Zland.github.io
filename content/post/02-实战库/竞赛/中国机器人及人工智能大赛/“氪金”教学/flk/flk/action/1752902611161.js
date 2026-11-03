Blockly.Blocks['1752902611161'] = {
  init: function() {
    this.jsonInit({
      "type": "1752902611161",
      "message0": "2f",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752902611161'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\nMOTOsetspeed(30)\nMOTOmove19(56,24,142,100,93,55,124,100,125,188,57,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(56,24,142,99,101,150,38,97,125,188,57,100,97,50,164,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(56,24,142,95,127,150,39,95,125,188,57,99,72,50,163,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(74,62,141,95,127,150,39,95,121,145,56,99,72,50,163,99,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(73,62,64,95,110,150,44,96,121,144,136,98,83,50,152,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752902611161'] = function(block) {
  let code = "robot.leju_action('2f')\n";
  return code;
}

