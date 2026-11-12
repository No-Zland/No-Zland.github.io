Blockly.Blocks['1752731348532'] = {
  init: function() {
    this.jsonInit({
      "type": "1752731348532",
      "message0": "叠块4",
      "previousStatement": "motion_block",
      "nextStatement": "motion_block",
      "colour": "#EDC611",
      "toolip": "",
      "helpUrl": ""
    });
  }
};

Blockly.Lua['1752731348532'] = function(block) {
  let code = "MOTOrigid16(40,40,40,40,40,40,40,40,40,40,40,40,40,40,40,40)\n\n\n-- 1\nMOTOsetspeed(30)\nMOTOmove19(58,24,171,100,93,55,130,98,123,188,31,100,107,145,70,102,120,40,100)\nMOTOwait()\n\n\n-- 2\nMOTOsetspeed(20)\nMOTOmove19(58,24,142,100,93,55,124,100,123,188,57,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(30)\nMOTOmove19(75,20,135,100,93,55,124,100,118,188,69,100,107,145,76,100,128,71,100)\nMOTOwait()\nMOTOsetspeed(5)\nMOTOmove19(75,20,135,98,100,69,106,96,118,188,69,99,98,126,96,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(15)\nMOTOmove19(74,69,134,98,100,69,106,96,117,139,68,99,98,126,96,98,128,71,100)\nMOTOwait()\nMOTOsetspeed(20)\nMOTOmove19(80,30,100,100,93,55,124,100,120,170,100,100,107,145,76,100,128,71,100)\nMOTOwait()\n";
  return code;
}

Blockly.Python['1752731348532'] = function(block) {
  let code = "robot.leju_action('叠块4')\n";
  return code;
}

