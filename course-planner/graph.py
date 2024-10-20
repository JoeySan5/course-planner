class Graph:
    class Node:
        def __init__(self, data, parents=None):
            self.data = data
            self.parents = parents
            self.children = []
            self.height = 0 if not parents else max(parent.height for parent in parents) + 1            
            self.selected = False

        def add_child(self, child_node):
            self.children.append(child_node)
            child_node.height = self.height + 1

        def __str__(self):
            return (f"Node(data: {self.data}, "
                    f"children: {[child.data for child in self.children]}, "
                    f"height: {self.height})")

    def __init__(self):
        self.root = self.Node(None)
        self.root.selected = True
        self.nodes = [self.root]
        self.size = 1
        self.id_set = set()

    def contains(self, data):
        return data.courseID in self.id_set

    def find_parents(self, parent_data_list):
        parents = []
        for parent_data in parent_data_list:
            for node in self.nodes:
                if node.data == parent_data:
                    parents.append(node)
                    break
        return parents

    def add_node(self, data, parent_data_list=[]):
        # Check if data already exists for some node. 
        # If it does, then immediately return
        if data.courseID in self.id_set:
            return
        parents = self.find_parents(parent_data_list) if parent_data_list else []
        if parents == []:
            parents = [self.root]
        new_node = self.Node(data, parents)
        self.id_set.add(data.courseID)
        print(f"Added course {data.courseID} in graph.")
        for parent in parents:
            parent.add_child(new_node)
        self.nodes.append(new_node)
        self.size += 1

    def select_node(self, node):
        node.selected = True

    def height_heuristic(self, node):
        return node.height
    
    def children_heuristic(self, node):
        return node.children
    
    # TODO: implement this heuristic
    # def subtree_heuristic(self, node):
    #     return node.height + len(node.children)
    
    def remaining_semesters_heuristic(self, node, semesters):
        course = node.data
        return len([semester for semester in semesters if course.offered_in_semester(semester)])

    def __str__(self):
        return '\n'.join(str(node) for node in self.nodes)