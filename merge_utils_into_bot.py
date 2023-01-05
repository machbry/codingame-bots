# import re
#
# with open("game.py", 'r') as reader:
#
#     lines_to_write = []
#     for line in reader.readlines():
#         custom_package_regex = re.compile("^from custom")
#         is_custom_package = custom_package_regex.match(line)
#         if is_custom_package is not None:
#             package_name_start = is_custom_package.end() + 1
#             package_name_end = re.compile("import").search(line).start() - 1
#             package_name = line[package_name_start:package_name_end]
#             with open("custom/"+package_name+".py", 'r') as package:
#                 package_lines = package.readlines()
#             lines_to_write.extend(package_lines)
#         else:
#             lines_to_write.append(line)
#
# with open("bots/my_bot.py", 'w') as writer:
#     for line in lines_to_write:
#         is_custom_package = custom_package_regex.match(line)
#         if is_custom_package is not None:
#             lines_to_write.remove(line)
#     writer.writelines(lines_to_write)