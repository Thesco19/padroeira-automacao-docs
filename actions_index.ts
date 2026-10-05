import academicSearchAction from './search/academicSearch';
import doneAction from './done';
import historySearchAction from './historySearch';
import osintAction from './osint';
import planAction from './plan';
import ActionRegistry from './registry';
import scrapeURLAction from './scrapeURL';
import socialSearchAction from './search/socialSearch';
import uploadsSearchAction from './uploadsSearch';
import webSearchAction from './search/webSearch';
import wikipediaAction from './wikipedia';
import atlasAction from './atlas';

ActionRegistry.register(webSearchAction);
ActionRegistry.register(doneAction);
ActionRegistry.register(planAction);
ActionRegistry.register(osintAction);
ActionRegistry.register(historySearchAction);
ActionRegistry.register(scrapeURLAction);
ActionRegistry.register(uploadsSearchAction);
ActionRegistry.register(academicSearchAction);
ActionRegistry.register(socialSearchAction);
ActionRegistry.register(wikipediaAction);
ActionRegistry.register(atlasAction);

export { ActionRegistry };
