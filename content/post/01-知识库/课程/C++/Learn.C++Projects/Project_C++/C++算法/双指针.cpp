//一、双指针核心概念
//双指针是一种通过维护两个指针（下标）在数据结构（如数组、链表）中高效遍历或解决问题的技巧，常用于优化时间复杂度或简化逻辑。
#include <bits/stdc++.h>
using namespace std;
//1.快慢指针
//用途：链表环检测、找链表中点、删除倒数第N个节点等。
//特点：两个指针步长不同（如快指针每次走2步，慢指针走1步）。
struct ListNode {
    int val;
    ListNode *next;
    ListNode(int x) : val(x), next(nullptr) {}
};

bool hasCycle(ListNode *head) {
    ListNode *slow = head, *fast = head;
    while (fast && fast->next) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;
    }
    return false;
}
//2.左右指针
//用途：有序数组的两数之和、反转数组、回文字符串判断。
//特点：指针分别从两端向中间移动，或从中间向两端扩散。
vector<int> twoSum(vector<int>& nums, int target) {
    int left = 0, right = nums.size() - 1;
    while (left < right) {
        int sum = nums[left] + nums[right];
        if (sum == target) return {left + 1, right + 1}; // 返回下标（非零基）
        else if (sum < target) left++;
        else right--;
    }
    return {}; // 无解
}
//3.前后指针
//用途：数组去重、原地删除元素（如LeetCode 27）。
//特点：一个指针遍历数组，另一个指针标记有效位置。
int removeElement(vector<int>& nums, int val) {
    int slow = 0;
    for (int fast = 0; fast < nums.size(); fast++) {
        if (nums[fast] != val) {
            nums[slow++] = nums[fast];
        }
    }
    return slow; // 返回新长度
}
//4.滑动窗口
//用途：子数组/子串问题（如最长无重复子串、最小覆盖子串）。
//特点：维护窗口的左右边界，动态调整窗口大小。
int lengthOfLongestSubstring(string s) {
    unordered_set<char> window;
    int left = 0, max_len = 0;
    for (int right = 0; right < s.size(); right++) {
        while (window.count(s[right])) { // 重复时收缩左边界
            window.erase(s[left]);
            left++;
        }
        window.insert(s[right]);
        max_len = max(max_len, right - left + 1);
    }
    return max_len;
}
// 四、应用场景总结
// 数组：去重、两数之和、反转、子数组问题。
// 链表：环检测、中点查找、合并链表。
// 字符串：回文判断、子串查找。
// 滑动窗口：连续区间问题（如最长/最短子串）。
// 五、注意事项
// 边界处理：指针移动时避免越界（如 fast->next 需非空）。
// 循环终止条件：左右指针需注意 left <= right 或 left < right。
// 步长选择：快慢指针的步长需根据问题调整（如2步或3步）。