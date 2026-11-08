Blockly.Blocks['1752581427936'] = {
  init: function() {
    this.jsonInit({
      "type": "1752581427936",
      "message0": "叠块go1",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752581427936'] = function(block) {
  let code = "MOTOrigid16(30,30,30,65,75,80,75,65,30,30,30,65,75,80,75,65)\nMOTOsetspeed(50)\nMOTOmove19(58,24,190,100,93,55,124,100,123,188,10,100,107,145,76,100,120,40,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(58,24,190,90,91,47,133,86,123,188,10,94,107,146,76,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(58,24,190,86,125,95,110,90,123,188,10,94,107,146,76,87,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,86,113,37,156,88,123,188,10,94,107,146,77,89,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(58,24,190,107,100,56,124,111,123,188,10,112,129,155,93,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,107,100,56,124,111,123,188,10,112,99,131,90,110,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,190,107,100,56,124,111,123,188,10,112,66,112,69,112,120,40,100)\nMOTOwait()\nMOTOsetspeed(10)\nMOTOmove19(58,24,190,109,95,63,117,100,123,188,10,112,97,114,95,102,120,40,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(58,24,189,100,93,55,124,100,123,188,10,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752581427936'] = function(block) {
  let code = "robot.leju_action('叠块go1')\n";
  return code;
}

