# category_controller.py
# Controller: checks the input and calls the model
# every method returns (success, result)

from src.models import category_model as model

MAX_GROUP_NAME = 50


class SearchGroupController:
    def __init__(self, user_id):
        self.user_id = user_id

    def check_group_name(self, name, exclude_id=0):
        # returns (name, error)
        name = (name or "").strip()
        if name == "":
            return None, "Category name cannot be empty."
        if len(name) > MAX_GROUP_NAME:
            return None, "Category name is too long (max 50 characters)."
        try:
            exists = model.group_name_exists(self.user_id, name, exclude_id)
        except Exception as e:
            return None, "Database error: " + str(e)
        if exists:
            return None, "This category name already exists."
        return name, None

    def search(self, keyword, group_id, sort_key, page, page_size):
        try:
            # ask for one extra row, so we know if there is a next page
            rows = model.search_contacts(
                self.user_id, keyword, group_id, sort_key,
                limit=page_size + 1, offset=page * page_size)
            has_next = len(rows) > page_size
            return True, (rows[:page_size], has_next)
        except Exception as e:
            return False, "Could not load contacts: " + str(e)

    def get_groups(self):
        try:
            return True, model.get_groups(self.user_id)
        except Exception as e:
            return False, "Could not load categories: " + str(e)

    def create_group(self, name):
        name, error = self.check_group_name(name)
        if error:
            return False, error
        try:
            model.create_group(self.user_id, name)
            return True, "Category created."
        except Exception as e:
            return False, "Database error, nothing was saved: " + str(e)

    def edit_group(self, group_id, new_name):
        new_name, error = self.check_group_name(new_name, group_id)
        if error:
            return False, error
        try:
            changed = model.rename_group(self.user_id, group_id, new_name)
            if changed == 0:
                return False, "Category not found."
            return True, "Category renamed."
        except Exception as e:
            return False, "Database error, the old name is kept: " + str(e)

    def delete_group(self, group_id):
        try:
            deleted = model.delete_group(self.user_id, group_id)
            if deleted == 0:
                return False, "Category not found."
            return True, "Category deleted. The contacts are still in your phone book."
        except Exception as e:
            return False, "Database error, nothing was deleted: " + str(e)

    def get_groups_of_contact(self, contact_id):
        try:
            return True, model.get_groups_of_contact(self.user_id, contact_id)
        except Exception as e:
            return False, "Could not load the groups of this contact: " + str(e)

    def assign_to_groups(self, contact_id, group_ids):
        if len(group_ids) == 0:
            return False, "Please choose at least one group."
        try:
            model.assign_contact_to_groups(self.user_id, contact_id, group_ids)
            return True, "Contact added to the group."
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, "Database error, nothing was saved: " + str(e)

    def remove_from_group(self, contact_id, group_id):
        try:
            removed = model.remove_contact_from_group(self.user_id, contact_id, group_id)
            if removed == 0:
                return False, "This contact is not in that group."
            return True, "Contact removed from the group."
        except Exception as e:
            return False, "Database error, nothing was removed: " + str(e)
