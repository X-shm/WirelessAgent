function verify_bluetooth_inventory()
%VERIFY_BLUETOOTH_INVENTORY Check registered public names against this MATLAB.
root=fileparts(fileparts(mfilename('fullpath')));
registry=jsondecode(fileread(fullfile(root,'tool_registry.json')));
names=strings(0,1);
for k=1:numel(registry.tools)
    if iscell(registry.tools), item=registry.tools{k};
    else, item=registry.tools(k); end
    if strcmp(item.product,'Bluetooth Toolbox')
        names=[names; string(item.source_functions(:))]; %#ok<AGROW>
    end
end
assert(numel(names)==52 && numel(unique(names))==52, ...
    'Bluetooth registry must have 52 distinct top-level names.');
missing=strings(0,1);
for k=1:numel(names)
    if isempty(which(char(names(k))))
        missing(end+1,1)=names(k); %#ok<AGROW>
    end
end
assert(isempty(missing),'Bluetooth source names unresolved: %s', ...
    strjoin(missing,', '));
fprintf('PASS %d distinct Bluetooth Toolbox top-level names resolve in MATLAB.\n', ...
    numel(names));
end
